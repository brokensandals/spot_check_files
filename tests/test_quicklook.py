from pathlib import Path
from PIL import Image
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


_IMGDIR = Path('tmp')


def setup_module(module):
    _IMGDIR.mkdir(exist_ok=True)


def test_supported():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            realpath=tmpdir.joinpath('text.csv'),
            tmpdir=tmpdir,
            virtpath='irrelevant'
        )
        req.realpath.write_text(_TEST_CSV)
        res1 = QLChecker().check(req)
        assert res1.recognizer
        assert res1.extracted is None
        assert res1.errors == []
        assert res1.thumb is None

        req.thumb = True
        res2 = QLChecker().check(req)
        assert res2.recognizer
        assert res2.extracted is None
        assert res2.errors == []
        res2.thumb.save(str(Path(_IMGDIR).joinpath('quicklook.png')))
        # I have no idea whether the Quick Look thumbnails are identical
        # across MacOS installations, let alone across different versions
        # of the OS, so this test may be extremely brittle
        with Image.open(str(Path('tests').joinpath('quicklook.png'))) as img:
            assert res2.thumb.tobytes() == img.tobytes()


def test_unsupported():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        req = CheckRequest(
            # omit file extension so QuickLook won't know what to do with it
            realpath=tmpdir.joinpath('text'),
            tmpdir=tmpdir,
            virtpath='irrelevant'
        )
        req.realpath.write_text(_TEST_CSV)
        res = QLChecker().check(req)
        assert res.recognizer is None
        assert res.extracted is None
        assert res.errors == ['no png produced by qlmanage']
        assert res.thumb is None
