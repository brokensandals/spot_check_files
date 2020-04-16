from io import BytesIO
from pathlib import Path
from spot_check_files.base import FileInfo
from spot_check_files.qlinspector import QLInspector


_TEST_CSV = """x,x^2,x^3
1,1,1
2,4,8
3,9,27
4,16,64
5,25,125
"""


def test_supported():
    data = BytesIO(bytes(_TEST_CSV, 'utf-8'))
    info = FileInfo(pathseq=('bogus.zip', 'foo/bar.csv'), size=100)
    QLInspector().inspect(info, lambda: data, thumbnail=True)
    assert info.problems == []
    assert info.recognized
    expected = Path('tests').joinpath(
        'qlinspector_expected_thumbnail.png').read_bytes()
    # I have no idea whether the Quick Look thumbnails are identical
    # across MacOS installations, let alone across different versions
    # of the OS, so this test may be extremely brittle
    assert info.thumbnail == expected


def test_thumbnail_not_requested():
    data = BytesIO(bytes(_TEST_CSV, 'utf-8'))
    info = FileInfo(pathseq=('bogus.zip', 'foo/bar.csv'), size=100)
    QLInspector().inspect(info, lambda: data)
    assert info.problems == []
    assert not info.recognized
    assert info.thumbnail is None


def test_unsupported():
    data = BytesIO(bytes(_TEST_CSV, 'utf-8'))
    # omit file extension so quicklook won't know what to do with it
    info = FileInfo(pathseq=('bogus.zip', 'foo/bar'), size=100)
    QLInspector().inspect(info, lambda: data, thumbnail=True)
    assert info.problems == []
    assert not info.recognized
    assert info.thumbnail is None
