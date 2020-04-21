from pathlib import Path
from tempfile import TemporaryDirectory
from spot_check_files.checker import CheckRequest
from spot_check_files.fileexts import FileExtChecker


def test_no_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.foo'))
        req.path.write_text('whatevs')
        res = FileExtChecker.default().check(req)
        assert res.recognizer is None
        assert res.errors == []


def test_failed_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(tmpdir=tmpdir, path=tmpdir.joinpath('test.zip'))
        req.path.write_text('whatevs')
        checker = FileExtChecker.default()
        res = checker.check(req)
        assert res.recognizer == checker
        assert res.errors == [
            'not a zipfile',
            'expected to be recognized by ZipFileChecker '
            'based on file extension'
        ]
