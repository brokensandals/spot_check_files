from io import BytesIO
import pytest
import zipfile
from spot_check_files.zipinspector import ZipInspector


def test_not_zip():
    data = BytesIO(bytes('garbage', 'utf-8'))
    with ZipInspector(data) as inspector:
        assert inspector.problems() == ['not a zipfile']
        assert inspector.filenames() == []
        with pytest.raises(KeyError):
            with inspector.extract('foo') as file:
                pass


def test_empty():
    data = BytesIO()
    with zipfile.ZipFile(data, 'w') as zf:
        pass
    with ZipInspector(data) as inspector:
        assert inspector.problems() == []
        assert inspector.filenames() == []
        with pytest.raises(KeyError):
            with inspector.extract('foo') as file:
                pass


def test_corrupt():
    data = BytesIO()
    with zipfile.ZipFile(data, 'w') as zf:
        zf.writestr('good.txt', 'nice to meet you!')
        zf.writestr('bad.txt', 'this works fine')
    data.seek(0)
    index = bytes(data.read()).find(bytes('work', 'utf-8'))
    data.seek(index)
    data.write(bytes('fail', 'utf-8'))
    with ZipInspector(data) as inspector:
        assert (inspector.problems()
                == ['zip contains at least one invalid entry: bad.txt'])
        assert inspector.filenames() == ['good.txt', 'bad.txt']


def test_valid():
    data = BytesIO()
    with zipfile.ZipFile(data, 'w') as zf:
        zf.writestr('alpha/file1', 'hello')
        zf.writestr('beta/file2', 'goodbye')
    with ZipInspector(data) as inspector:
        assert inspector.problems() == []
        assert inspector.filenames() == ['alpha/file1', 'beta/file2']
        with inspector.extract('alpha/file1') as file:
            assert str(file.read(), 'utf-8') == 'hello'
        with inspector.extract('beta/file2') as file:
            assert str(file.read(), 'utf-8') == 'goodbye'
        with pytest.raises(KeyError):
            with inspector.extract('foo') as file:
                pass
