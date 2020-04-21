from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from spot_check_files.archives import TarChecker, ZipChecker
from spot_check_files.checker import CheckRequest


def test_not_zip():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.zip'),
            tmpdir=tmpdir,
            virtpath='irrelevant')
        req.realpath.write_text('garbage')
        res = ZipChecker().check(req)
        assert res.recognizer is None
        assert res.extracted is None
        assert res.errors == ['not a zipfile']


def test_empty_zip():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.zip'),
            tmpdir=tmpdir,
            virtpath='irrelevant')
        with ZipFile(req.realpath, 'w') as zf:
            pass
        res = ZipChecker().check(req)
        assert res.recognizer
        assert res.extracted
        assert list(res.extracted.glob('**/*')) == []
        assert res.errors == []


def test_corrupt_zip():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.zip'),
            tmpdir=tmpdir,
            virtpath='irrelevant')
        with ZipFile(req.realpath, 'w') as zf:
            zf.writestr('good.txt', 'nice to meet you!')
            zf.writestr('bad.txt', 'this works fine')
        old = req.realpath.read_bytes()
        corrupt = old.replace(bytes('work', 'utf-8'), bytes('fail', 'utf-8'))
        req.realpath.write_bytes(corrupt)
        res = ZipChecker().check(req)
        assert res.recognizer
        assert res.extracted
        assert ([p.name for p in res.extracted.glob('**/*')]
                == ['good.txt', 'bad.txt'])
        assert ([str(e) for e in res.errors]
                == ["Bad CRC-32 for file 'bad.txt'"])


def test_valid_zipfile():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.zip'),
            tmpdir=tmpdir,
            virtpath='irrelevant')
        with ZipFile(req.realpath, 'w') as zf:
            zf.writestr('good.txt', 'nice to meet you!')
            zf.writestr('bad.txt', 'this works fine')
        res = ZipChecker().check(req)
        assert res.recognizer
        assert res.extracted
        assert ([p.name for p in res.extracted.glob('**/*')]
                == ['good.txt', 'bad.txt'])
        assert ([p.read_text() for p in res.extracted.glob('**/*')]
                == ['nice to meet you!', 'this works fine'])
        assert res.errors == []


def test_not_tarfile():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.tar'),
            tmpdir=tmpdir,
            virtpath='irrelevant')
        req.realpath.write_text('garbage')
        res = TarChecker().check(req)
        assert res.recognizer is None
        assert res.extracted is None
        assert res.errors == ['not a tarfile']


def test_corrupt_tarfile():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.tar'),
            tmpdir=tmpdir,
            virtpath='irrelevant')

        dir1 = tmpdir.joinpath('alpha')
        dir1.mkdir()
        dir2 = tmpdir.joinpath('beta')
        dir2.mkdir()
        dir1.joinpath('file1').write_text('hello' * 10)
        dir2.joinpath('file2').write_text('goodbye' * 10)
        with tarfile.open(req.realpath, 'w:gz') as tf:
            tf.add(dir1, 'alpha')
            tf.add(dir2, 'beta')
        data = bytearray(req.realpath.read_bytes())
        data[30] = 10
        req.realpath.write_bytes(data)

        res = TarChecker().check(req)
        assert res.recognizer is None  # TODO perhaps should be set
        assert res.extracted is None
        assert len(res.errors) == 1
        assert 'Error -3' in str(res.errors[0])


def test_valid_tarfile():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('test.tar'),
            tmpdir=tmpdir,
            virtpath='irrelevant')

        dir1 = tmpdir.joinpath('alpha')
        dir1.mkdir()
        dir2 = tmpdir.joinpath('beta')
        dir2.mkdir()
        dir1.joinpath('file1').write_text('hello' * 10)
        dir2.joinpath('file2').write_text('goodbye' * 10)

        def test_compression(compression):
            with tarfile.open(req.realpath, f'w:{compression}') as tf:
                tf.add(dir1, 'alpha')
                tf.add(dir2, 'beta')

            res = TarChecker().check(req)
            assert res.recognizer
            assert res.extracted
            paths = [p for p in res.extracted.glob('**/*') if p.is_file()]
            assert len(paths) == 2
            path1 = res.extracted.joinpath('alpha', 'file1')
            path2 = res.extracted.joinpath('beta', 'file2')
            assert path1 in paths
            assert path2 in paths
            assert path1.read_text() == 'hello' * 10
            assert path2.read_text() == 'goodbye' * 10
            assert res.errors == []

            req.realpath.unlink()

        test_compression('')
        test_compression('gz')
        test_compression('bz2')
        test_compression('xz')
