from io import BytesIO
from pathlib import Path
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
    inspector = QLInspector(data, ('foo/bar.csv',))
    assert inspector.filenames() == []
    assert inspector.problems() == []
    thumbnail = inspector.thumbnail()
    expected = Path('tests').joinpath(
        'qlinspector_expected_thumbnail.png').read_bytes()
    # I have no idea whether the Quick Look thumbnails are identical
    # across MacOS installations, let alone across different versions
    # of the OS, so this test may be extremely brittle
    assert thumbnail == expected
