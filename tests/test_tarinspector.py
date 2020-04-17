from io import BytesIO
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from spot_check_files.base import FileInfo, IOFileAccessor
from spot_check_files.tarinspector import ExtractingTarInspector,\
    StreamingTarInspector


_inspectors = [ExtractingTarInspector(), StreamingTarInspector()]
_compressions = ['', 'gz', 'bz2', 'xz']


def test_not_tar():
    for inspector in _inspectors:
        data = BytesIO(bytes('garbage', 'utf-8'))
        info = FileInfo(pathseq=('test.tar',), size=100)
        acc = IOFileAccessor(info.pathseq, lambda: data)
        inspector.inspect(info, acc)
        assert info.problems
        assert not info.recognized
        assert not info.mere_container


def test_corrupt():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        dir1 = tmpdir.joinpath('alpha')
        dir1.mkdir()
        dir2 = tmpdir.joinpath('beta')
        dir2.mkdir()
        dir1.joinpath('file1').write_text('hello' * 10)
        dir2.joinpath('file2').write_text('goodbye' * 10)
        for inspector in _inspectors:
            data = BytesIO()
            with tarfile.open(mode='w:gz', fileobj=data) as tf:
                tf.add(dir1, 'alpha')
                tf.add(dir2, 'beta')
            data.seek(30)
            data.write(bytes(10))
            data.seek(0)
            info = FileInfo(pathseq=('test.tar',), size=100)
            acc = IOFileAccessor(info.pathseq, lambda: data)
            inspector.inspect(info, acc)
            assert info.problems == ['error while inspecting']


def test_valid():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        dir1 = tmpdir.joinpath('alpha')
        dir1.mkdir()
        dir2 = tmpdir.joinpath('beta')
        dir2.mkdir()
        dir1.joinpath('file1').write_text('hello' * 10)
        dir2.joinpath('file2').write_text('goodbye' * 10)
        for inspector in _inspectors:
            for compression in _compressions:
                data = BytesIO()
                with tarfile.open(mode=f'w:{compression}', fileobj=data) as tf:
                    tf.add(dir1, 'alpha')
                    tf.add(dir2, 'beta')
                data.seek(0)
                info = FileInfo(pathseq=('test.tar',), size=100)
                acc = IOFileAccessor(info.pathseq, lambda: data)

                children = []
                children_data = {}

                def on_child(child_info, child_acc):
                    children.append(child_info)
                    with child_acc.io() as child_data:
                        children_data[child_info.pathseq] =\
                            str(child_data.read(), 'utf-8')

                inspector.inspect(info, acc, on_child=on_child)
                assert info.problems == []
                assert info.recognized
                assert info.mere_container

                # the streaming inspector will go in order of the archive, but
                # the extracting inspector depends on the order of Path.glob,
                # so this test can't assume a particular order
                assert len(children) == 2
                assert (FileInfo(pathseq=('test.tar', 'alpha/file1'), size=50)
                        in children)
                assert (FileInfo(pathseq=('test.tar', 'beta/file2'), size=70)
                        in children)
                assert children_data == {
                    ('test.tar', 'alpha/file1'): 'hello' * 10,
                    ('test.tar', 'beta/file2'): 'goodbye' * 10,
                }
