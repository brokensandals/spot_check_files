from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from spot_check_files.archives import ZipChecker
from spot_check_files.checker import CheckRequest


def test_not_zip():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        req.path.write_text('garbage')
        res = ZipChecker().check(req)
        assert not res.identified
        assert res.extracted is None
        assert res.errors == ['not a zipfile']


def test_empty_zip():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        with ZipFile(req.path, 'w') as zf:
            pass
        res = ZipChecker().check(req)
        assert res.identified
        assert res.extracted
        assert list(res.extracted.glob('**/*')) == []
        assert res.errors == []


def test_corrupt_zip():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        with ZipFile(req.path, 'w') as zf:
            zf.writestr('good.txt', 'nice to meet you!')
            zf.writestr('bad.txt', 'this works fine')
        old = req.path.read_bytes()
        corrupt = old.replace(bytes('work', 'utf-8'), bytes('fail', 'utf-8'))
        req.path.write_bytes(corrupt)
        res = ZipChecker().check(req)
        assert res.identified
        assert res.extracted
        assert ([p.name for p in res.extracted.glob('**/*')]
                == ['good.txt', 'bad.txt'])
        assert ([str(e) for e in res.errors]
                == ["Bad CRC-32 for file 'bad.txt'"])


def test_valid():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        with ZipFile(req.path, 'w') as zf:
            zf.writestr('good.txt', 'nice to meet you!')
            zf.writestr('bad.txt', 'this works fine')
        res = ZipChecker().check(req)
        assert res.identified
        assert res.extracted
        assert ([p.name for p in res.extracted.glob('**/*')]
                == ['good.txt', 'bad.txt'])
        assert ([p.read_text() for p in res.extracted.glob('**/*')]
                == ['nice to meet you!', 'this works fine'])
        assert res.errors == []
