from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from spot_check_files.base import FileInfo, IOFileAccessor, FSFileAccessor
from spot_check_files.xmlinspector import XMLInspector


def test_invalid():
    data = BytesIO(bytes('<hello></garbage>', 'utf-8'))
    info = FileInfo(pathseq=('test.xml',), size=100)
    acc = IOFileAccessor(info.pathseq, lambda: data)
    XMLInspector().inspect(info, acc)
    assert info.problems == ['invalid xml']
    assert not info.recognized


def test_valid():
    data = BytesIO(bytes('<hello>yay</hello>', 'utf-8'))
    info = FileInfo(pathseq=('test.xml',), size=100)
    acc = IOFileAccessor(info.pathseq, lambda: data)
    XMLInspector().inspect(info, acc)
    assert info.problems == []
    assert info.recognized


def test_from_file():
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir).joinpath('test.xml')
        path.write_text('<hello>yay</hello>')
        info = FileInfo(pathseq=('test.xml',), size=100)
        acc = FSFileAccessor(path)
        XMLInspector().inspect(info, acc)
        assert info.problems == []
        assert info.recognized
