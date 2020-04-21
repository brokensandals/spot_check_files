from pathlib import Path
from tempfile import TemporaryDirectory
from spot_check_files.basics import PlaintextChecker
from spot_check_files.checker import CheckRequest


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
