from pathlib import Path
from tempfile import TemporaryDirectory
from spot_check_files.checker import CheckRequest
from spot_check_files.quicklook import QLChecker


_TEST_CSV = """x,x^2,x^3
1,1,1
2,4,8
3,9,27
4,16,64
5,25,125
"""


def test_supported():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            tmpdir=tmpdir,
            path=tmpdir.joinpath('text.csv')
        )
        req.path.write_text(_TEST_CSV)
        res1 = QLChecker().check(req)
        assert res1.identified
        assert res1.extracted is None
        assert res1.errors == []
        assert res1.png is None

        req.png = True
        res2 = QLChecker().check(req)
        assert res2.identified
        assert res2.extracted is None
        assert res2.errors == []
        expected = Path('tests').joinpath('quicklook.png').read_bytes()
        assert res2.png == expected
