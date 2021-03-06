import json
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from tempfile import TemporaryDirectory
from spot_check_files.basics import CSVChecker, ImageChecker,\
    JSONChecker, PlaintextChecker, XMLChecker
from spot_check_files.checker import CheckRequest


_TEST_CSV = """x,x^2,x cubed in words,x^3
1,1,one,1
2,4,eight,8
3,9,twenty-seven,27
4,16,sixteen,64
5,25,one hundred and twenty-five,125
"""


_TEST_JSON = """{"hello": {
  "nicely_formatted": false, "valid": true,
  "array": [1, 2, 3, 4, 5, 6, 7, 8, 9,
    "This is a multiline string.\\nHuzzah."]
}
}"""


_TEST_XML = """<root><one>Hello there
</one><one>How are you?</one><two>I am
not dead (at time of writing).</two></root>"""


_IMGDIR = Path('tmp')


def setup_module(module):
    _IMGDIR.mkdir(exist_ok=True)


def test_csv_valid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.csv'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text(_TEST_CSV)
        res = CSVChecker().check(req)
        assert isinstance(res.recognizer, CSVChecker)
        assert res.errors == []
        assert res.thumb is None

        req.thumb = True
        res = CSVChecker().check(req)
        assert res.errors == []
        res.thumb.save(str(Path(_IMGDIR).joinpath('csv.png')))
        with Image.open(str(Path('tests').joinpath('csv.png'))) as img:
            assert res.thumb.tobytes() == img.tobytes()


def test_csv_missing_cols():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.csv'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text('a,b,c\n1,2')
        res = CSVChecker().check(req)
        assert res.recognizer is None
        assert len(res.errors) == 1
        assert str(res.errors[0]) == 'Could not determine delimiter'


def test_tsv():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.tsv'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.thumb = True
        req.realpath.write_text(_TEST_CSV.replace(',', '\t'))
        res = CSVChecker().check(req)
        assert isinstance(res.recognizer, CSVChecker)
        assert res.errors == []
        res.thumb.save(str(Path(_IMGDIR).joinpath('tsv.png')))
        with Image.open(str(Path('tests').joinpath('csv.png'))) as img:
            assert res.thumb.tobytes() == img.tobytes()


def test_image_valid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=Path('tests').joinpath('testimage.jpg'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        res = ImageChecker().check(req)
        assert isinstance(res.recognizer, ImageChecker)
        assert res.errors == []
        assert res.thumb is None

        req.thumb = True
        res = ImageChecker().check(req)
        assert res.errors == []
        res.thumb.save(str(Path(_IMGDIR).joinpath('image.png')))
        with Image.open(Path('tests').joinpath('image.png')) as img:
            assert res.thumb.tobytes() == img.tobytes()


def test_image_invalid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.jpg'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text('garbage')
        res = ImageChecker().check(req)
        assert res.recognizer is None
        assert len(res.errors) == 1
        assert isinstance(res.errors[0], UnidentifiedImageError)
        assert res.thumb is None


def test_json_valid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.json'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text(_TEST_JSON)
        res = JSONChecker().check(req)
        assert isinstance(res.recognizer, JSONChecker)
        assert res.errors == []
        assert res.thumb is None

        req.thumb = True
        res = JSONChecker().check(req)
        assert res.errors == []
        res.thumb.save(str(Path(_IMGDIR).joinpath('json.png')))
        with Image.open(Path('tests').joinpath('json.png')) as img:
            assert res.thumb.tobytes() == img.tobytes()


def test_json_invalid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.json'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text('{"garbage": true')
        res = JSONChecker().check(req)
        assert res.recognizer is None
        assert len(res.errors) == 1
        assert isinstance(res.errors[0], json.JSONDecodeError)


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
        assert res.thumb is None

        req.thumb = True
        res = PlaintextChecker().check(req)
        assert res.errors == []
        res.thumb.save(str(Path(_IMGDIR).joinpath('plaintext.png')))
        # The font I'm currently using doesn't handle emoji but I don't
        # really care right now
        with Image.open(str(Path('tests').joinpath('plaintext.png'))) as img:
            assert res.thumb.tobytes() == img.tobytes()


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
        assert res.thumb is None


def test_xml_valid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.xml'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text(_TEST_XML)
        res = XMLChecker().check(req)
        assert isinstance(res.recognizer, XMLChecker)
        assert res.errors == []
        assert res.thumb is None

        req.thumb = True
        res = XMLChecker().check(req)
        assert res.errors == []
        res.thumb.save(str(Path(_IMGDIR).joinpath('xml.png')))
        with Image.open(Path('tests').joinpath('xml.png')) as img:
            assert res.thumb.tobytes() == img.tobytes()


def test_xml_invalid():
    with TemporaryDirectory() as td:
        td = Path(td)
        req = CheckRequest(
            realpath=td.joinpath('test.xml'),
            tmpdir=td,
            virtpath=Path('irrelevant'))
        req.realpath.write_text('<root>garbage')
        res = XMLChecker().check(req)
        assert res.recognizer is None
        assert len(res.errors) == 1
        assert 'no element found' in str(res.errors[0])
