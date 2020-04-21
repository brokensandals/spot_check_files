from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from spot_check_files.archives import ZipChecker
from spot_check_files.basics import CSVChecker, PlaintextChecker
from spot_check_files.checker import CheckerRunner


def test_check_path_single_file():
    with TemporaryDirectory() as td:
        td = Path(td)
        fpath = td.joinpath('test.csv')
        fpath.write_text('a,b,c\n1,2,3')
        cr = CheckerRunner.default()
        s = cr.check_path(fpath)
        assert len(s) == 1
        assert s[0].size == 11
        assert s[0].virtpath == fpath
        assert isinstance(s[0].result.recognizer, CSVChecker)
        assert s[0].result.errors == []


def test_check_path_dir():
    with TemporaryDirectory() as td:
        td = Path(td)
        fpath1 = td.joinpath('test.csv')
        fpath1.write_text('a,b,c\n1,2,3')
        fpath2 = td.joinpath('test.zip')
        with ZipFile(fpath2, 'w') as zf:
            zf.writestr('alpha/file1.txt', 'hello')
            zf.writestr('beta/file2.txt', 'goodbye')
        vpath3 = fpath2.joinpath('alpha', 'file1.txt')
        vpath4 = fpath2.joinpath('beta', 'file2.txt')
        cr = CheckerRunner.default()
        s = cr.check_path(td)
        s.sort(key=lambda x: x.virtpath.name)
        assert len(s) == 4
        assert s[2].size == 11
        assert s[2].virtpath == fpath1
        assert isinstance(s[2].result.recognizer, CSVChecker)
        assert s[2].result.errors == []
        assert s[3].size == fpath2.stat().st_size
        assert s[3].virtpath == fpath2
        assert isinstance(s[3].result.recognizer, ZipChecker)
        assert s[3].result.errors == []
        assert s[0].size == 5
        assert s[0].virtpath == vpath3
        assert isinstance(s[0].result.recognizer, PlaintextChecker)
        assert s[0].result.errors == []
        assert s[1].size == 7
        assert s[1].virtpath == vpath4
        assert isinstance(s[1].result.recognizer, PlaintextChecker)
        assert s[1].result.errors == []
