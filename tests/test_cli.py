import os
from pathlib import Path
import pytest
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from spot_check_files import cli


_SAMPLE_CSV = """x,x^2,x^3,x^4,x to the fourth in English
1,1,1,1,one
2,4,8,16,sixteen
3,9,27,81,eighty-one
4,16,64,256,two hundred fifty-six
5,25,125,625,six hundred twenty-five
6,36,216,1296,one thousand two hundred ninety-six
7,49,343,2401,two thousand four hundred and one
8,64,512,4096,four thousand ninety-six
9,81,729,6561,six thousand five hundred sixty-one
"""


_TMPDIR = Path('tmp')


def setup_module(module):
    _TMPDIR.mkdir(exist_ok=True)


def test_help(capsys):
    with pytest.raises(SystemExit):
        cli.main(['-h'])
    cap = capsys.readouterr()
    out = re.sub(r'\S*pytest\S*', 'spotcheck', cap.out)
    Path('doc').joinpath('usage.txt').write_text(out)


def test_happy_path(capsys):
    with TemporaryDirectory() as td:
        zp = Path(td).joinpath('test.zip')
        with ZipFile(zp, 'w') as zf:
            zf.writestr('sample.csv', _SAMPLE_CSV)
            zf.write(Path('tests').joinpath('testimage.jpg'))
            zf.writestr('sample.json', '{"sample_data": [1, 2, 3, 4, 5]}')
            zf.write(Path('tests').joinpath('image.png'), 'test.xml')
        oldwd = os.getcwd()
        try:
            # chdir so when we print the output to doc/, it won't
            # include the path to the temporary directory
            os.chdir(td)
            assert cli.main(['.']) == 0
            cap = capsys.readouterr()
            text = cap.out
            assert cli.main(['-H', '.']) == 0
            cap = capsys.readouterr()
            html = cap.out
        finally:
            os.chdir(oldwd)
        Path('doc').joinpath('sample-out.txt').write_text(text)
        Path('doc').joinpath('sample-out.html').write_text(html)
        zp.rename(_TMPDIR.joinpath('test.zip'))


def test_skip(capsys):
    with TemporaryDirectory() as td:
        zp = Path(td).joinpath('test.zip')
        with ZipFile(zp, 'w') as zf:
            zf.writestr('yes.txt', '1')
            zf.writestr('no.txt', 'one')
            zf.writestr('bad.json', '{')
        assert cli.main([td, '-s', 'yes.txt',
                         '-s', str(zp.joinpath('no*')),
                         '-s', '*.json']) == 0
        cap = capsys.readouterr()
        assert re.search(r'^.*Skipped files.*\b67%.*\b80%.*$',
                         cap.out, re.MULTILINE)
