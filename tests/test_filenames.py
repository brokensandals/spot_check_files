from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from spot_check_files.archives import ZipChecker
from spot_check_files.checker import CheckRequest
from spot_check_files.filenames import FileNameChecker


def test_no_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.foo'))
        req.path.write_text('whatevs')
        res = FileNameChecker.default().check(req)
        assert res.recognizer is None
        assert res.errors == []


def test_failed_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        req.path.write_text('whatevs')
        checker = FileNameChecker.default()
        res = checker.check(req)
        assert res.recognizer == checker
        assert res.errors == [
            'not a zipfile',
            'expected to be recognized by ZipChecker '
            'because filename matched: *.zip'
        ]


def test_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        with ZipFile(req.path, 'w') as zf:
            pass
        res = FileNameChecker.default().check(req)
        assert isinstance(res.recognizer, ZipChecker)
        assert res.errors == []
        assert res.extracted
