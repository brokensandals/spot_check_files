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


def _assert_sample_inspect(vpath, checker):
    assert checker.vpaths == [
        vpath,
        vpath + ('folder/file1.json',),
        vpath + ('folder/file2.txt',),
        vpath + ('nested.zip',),
        vpath + ('nested.zip', 'file3.xml'),
        vpath + ('nested.zip', 'garbage.json'),
        vpath + ('garbage.zip',),
    ]

    assert checker.problems == {
        vpath + ('garbage.zip',): ['not a zipfile'],
        vpath + ('nested.zip', 'garbage.json'): ['invalid json'],
    }

    assert ([t[0] for t in checker.thumbnails]
            == [vpath + ('folder/file2.txt',),
                vpath + ('nested.zip', 'file3.xml')])


def test_inspect_pathlike():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        path = tmpdir.joinpath('sample.zip')
        path.write_bytes(_make_sample_zip())

        for variant in [path, str(path)]:
            checker = Checker(num_thumbnails=10)
            checker.check(variant)
            _assert_sample_inspect((str(path),), checker)


def test_inspect_filelike():
    data = BytesIO(_make_sample_zip())
    checker = Checker(num_thumbnails=10)
    checker.check(data, ('foo.zip',))
    _assert_sample_inspect(('foo.zip',), checker)
