from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from spot_check_files.archives import ZipChecker
from spot_check_files.basics import PlaintextChecker
from spot_check_files.checker import CheckRequest
from spot_check_files.filenames import FileNameChecker


def test_no_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            tmpdir=tmpdir,
            realpath=tmpdir.joinpath('test'),
            virtpath='test.foo')
        req.realpath.write_text('whatevs')
        res = FileNameChecker.default().check(req)
        assert res.recognizer is None
        assert res.errors == []


def test_failed_match():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            tmpdir=tmpdir,
            realpath=tmpdir.joinpath('test'),
            virtpath='test.zip')
        req.realpath.write_text('whatevs')
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
        req = CheckRequest(
            tmpdir=tmpdir,
            realpath=tmpdir.joinpath('test'),
            virtpath='test.zip')
        with ZipFile(req.realpath, 'w') as zf:
            pass
        res = FileNameChecker.default().check(req)
        assert isinstance(res.recognizer, ZipChecker)
        assert res.errors == []
        assert res.extracted


def test_blacklist():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        path = tmpdir.joinpath('test')
        path.write_text('hello')
        req = CheckRequest(
            tmpdir=tmpdir,
            realpath=path,
            virtpath='test.zip/yes.txt')
        checker = FileNameChecker.default()
        checker.blacklist.append('test.zip/no.*')
        res = checker.check(req)
        assert isinstance(res.recognizer, PlaintextChecker)
        assert res.errors == []
        assert not res.skipped
        req.virtpath = 'test.zip/no.txt'
        res = checker.check(req)
        assert res.recognizer is checker
        assert res.errors == []
        assert res.skipped
