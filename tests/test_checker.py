from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile
from spot_check_files.checker import Checker


def _make_sample_zip():
    data = BytesIO()
    with zipfile.ZipFile(data, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('folder/file1.json', '{"happy": true}')
        zf.writestr('folder/file2.txt', 'melancholy')

        data2 = BytesIO()
        with zipfile.ZipFile(
                data2, 'w', compression=zipfile.ZIP_DEFLATED) as zf2:
            zf2.writestr('file3.xml', '<stuff><thing /></stuff>')
            zf2.writestr('garbage.json', '{"sad": ')
        data2.seek(0)
        zf.writestr('nested.zip', data2.read())

        zf.writestr('garbage.zip', bytes())
    data.seek(0)
    return data.read()


def _assert_sample_inspect(pathseq, checker):
    assert {i.pathseq: i.problems for i in checker.files if i.problems} == {
        pathseq + ('garbage.zip',): ['not a zipfile'],
        pathseq + ('nested.zip', 'garbage.json'): ['invalid json'],
    }

    assert len(checker.files) == 7

    assert sorted([i.pathseq for i in checker.files]) == [
        pathseq,
        pathseq + ('folder/file1.json',),
        pathseq + ('folder/file2.txt',),
        pathseq + ('garbage.zip',),
        pathseq + ('nested.zip',),
        pathseq + ('nested.zip', 'file3.xml'),
        pathseq + ('nested.zip', 'garbage.json'),
    ]

    assert (sorted([i.pathseq for i in checker.thumbnail_files])
            == [pathseq + ('folder/file2.txt',)])


def test_check_path():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        path = tmpdir.joinpath('sample.zip')
        path.write_bytes(_make_sample_zip())
        checker = Checker(num_thumbnails=10)
        checker.check_path(str(path))
        _assert_sample_inspect((str(path),), checker)
