from pathlib import Path
from tempfile import TemporaryDirectory
from spot_check_files.basics import CSVChecker, PlaintextChecker
from spot_check_files.checker import CheckRequest


_TEST_CSV = """x,x^2,x cubed in words,x^3
1,1,one,1
2,4,eight,8
3,9,twenty-seven,27
4,16,sixteen,64
5,25,one hundred and twenty-five,125
"""


def test_csv_valid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.csv'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text(_TEST_CSV)
        res = CSVChecker().check(req)
        assert isinstance(res.recognizer, CSVChecker)
        assert res.errors == []
        assert res.png is None

        req.png = True
        res = CSVChecker().check(req)
        assert res.errors == []
        expected = Path('tests').joinpath('csv.png').read_bytes()
        assert res.png == expected


def test_plaintext_valid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.txt'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text('Hello, world!😀\nNo problems here!\n')
        res = PlaintextChecker().check(req)
        assert isinstance(res.recognizer, PlaintextChecker)
        assert res.errors == []
        assert res.png is None

        req.png = True
        res = PlaintextChecker().check(req)
        assert res.errors == []
        # The font I'm currently using doesn't handle emoji but I don't
        # really care right now
        expected = Path('tests').joinpath('plaintext.png').read_bytes()
        assert res.png == expected


def test_plaintext_encoding_error():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.txt'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_bytes(
            bytes('Hello, world!', 'utf-8')
            + bytes([0xfe]) + bytes('oops', 'utf-8'))
        res = PlaintextChecker().check(req)
        assert isinstance(res.recognizer, PlaintextChecker)
        assert len(res.errors) == 1
        assert isinstance(res.errors[0], UnicodeDecodeError)
        assert res.png is None
