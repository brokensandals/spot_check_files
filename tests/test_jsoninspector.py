from io import BytesIO
from spot_check_files.base import FileInfo
from spot_check_files.jsoninspector import JSONInspector


def test_invalid():
    data = BytesIO(bytes('garbage', 'utf-8'))
    info = FileInfo(pathseq=('test.json',), size=100)
    JSONInspector().inspect(info, lambda: data)
    assert info.problems == ['invalid json']
    assert not info.recognized


def test_valid():
    data = BytesIO(bytes('{"garbage": false}', 'utf-8'))
    info = FileInfo(pathseq=('test.json',), size=100)
    JSONInspector().inspect(info, lambda: data)
    assert info.problems == []
    assert info.recognized
