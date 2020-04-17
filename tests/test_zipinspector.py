from io import BytesIO
import zipfile
from spot_check_files.base import FileInfo, IOFileAccessor
from spot_check_files.zipinspector import ExtractingZipInspector,\
    StreamingZipInspector


_inspectors = [ExtractingZipInspector(), StreamingZipInspector()]


def test_not_zip():
    for inspector in _inspectors:
        data = BytesIO(bytes('garbage', 'utf-8'))
        info = FileInfo(pathseq=('test.zip',), size=100)
        acc = IOFileAccessor(info.pathseq, lambda: data)
        inspector.inspect(info, acc)
        assert info.problems == ['not a zipfile']
        assert not info.recognized
        assert not info.mere_container


def test_empty():
    for inspector in _inspectors:
        data = BytesIO()
        with zipfile.ZipFile(data, 'w') as zf:
            pass
        info = FileInfo(pathseq=('test.zip',), size=100)
        acc = IOFileAccessor(info.pathseq, lambda: data)
        inspector.inspect(info, acc)
        assert info.problems == []
        assert info.recognized
        assert info.mere_container


def test_corrupt():
    for inspector in _inspectors:
        data = BytesIO()
        with zipfile.ZipFile(data, 'w') as zf:
            zf.writestr('good.txt', 'nice to meet you!')
            zf.writestr('bad.txt', 'this works fine')
        data.seek(0)
        index = bytes(data.read()).find(bytes('work', 'utf-8'))
        data.seek(index)
        data.write(bytes('fail', 'utf-8'))

        info = FileInfo(pathseq=('test.zip',), size=100)
        children = []
        children_data = []

        def on_child(child_info, child_acc):
            children.append(child_info)
            with child_acc.io() as child_data:
                children_data.append(str(child_data.read(), 'utf-8'))

        acc = IOFileAccessor(info.pathseq, lambda: data)
        inspector.inspect(info, acc, on_child=on_child)
        assert info.problems == ['zip contains at least one invalid entry']
        assert info.recognized
        assert info.mere_container

        if isinstance(inspector, StreamingZipInspector):
            assert children == [
                FileInfo(pathseq=('test.zip', 'good.txt'), size=17),
                FileInfo(pathseq=('test.zip', 'bad.txt'), size=15,
                         problems=['corrupt in zip']),
            ]
            assert children_data == ['nice to meet you!']
        else:
            assert children == []
            assert children_data == []


def test_valid():
    for inspector in _inspectors:
        data = BytesIO()
        with zipfile.ZipFile(data, 'w') as zf:
            zf.writestr('alpha/file1', 'hello')
            zf.writestr('beta/file2', 'goodbye')

        info = FileInfo(pathseq=('test.zip',), size=100)
        children = []
        children_data = {}

        def on_child(child_info, child_acc):
            children.append(child_info)
            with child_acc.io() as child_data:
                children_data[child_info.pathseq] =\
                    str(child_data.read(), 'utf-8')

        acc = IOFileAccessor(info.pathseq, lambda: data)
        inspector.inspect(info, acc, on_child=on_child)
        assert info.problems == []
        assert info.recognized
        assert info.mere_container
        # the streaming inspector will go in order of the archive, but
        # the extracting inspector depends on the order of Path.glob,
        # so this test can't assume a particular order
        assert len(children) == 2
        assert (FileInfo(pathseq=('test.zip', 'alpha/file1'), size=5)
                in children)
        assert (FileInfo(pathseq=('test.zip', 'beta/file2'), size=7)
                in children)
        assert children_data == {
            ('test.zip', 'alpha/file1'): 'hello',
            ('test.zip', 'beta/file2'): 'goodbye',
        }
