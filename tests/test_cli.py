from pathlib import Path
import pytest
import re
from tempfile import TemporaryDirectory
from spot_check_files import cli


def test_help(capsys):
    doc = Path('doc')
    with pytest.raises(SystemExit):
        cli.main(['-h'])
    cap = capsys.readouterr()
    doc.joinpath('usage.txt').write_text(
        re.sub(r'\S*pytest\S*', 'spot_check_files', cap.out))


def test_no_problems(capsys):
    with TemporaryDirectory() as tmpdir:
        Path(tmpdir).joinpath('ok.json').write_text('{"happy": true}')
        assert cli.main([tmpdir]) == 0
        cap = capsys.readouterr()
        assert 'Total files: 1\n' in cap.out
        assert 'Recognized 100% of files, 100% by size\n' in cap.out
        assert 'Made thumbnails of 0% of files, 0% by size\n' in cap.out


def test_problems(capsys):
    with TemporaryDirectory() as tmpdir:
        tmpdirpath = Path(tmpdir)
        pathbad = tmpdirpath.joinpath('bad.json')
        pathbad.write_text('{"happy": }')
        pathok = tmpdirpath.joinpath('ok.json')
        pathok.write_text('{"happy": true}')
        pathterrible = tmpdirpath.joinpath('terrible.json')
        pathterrible.write_text('{"happy": nope}')
        assert cli.main([tmpdir]) == 0
        cap = capsys.readouterr()
        assert 'Total files: 3\n' in cap.out
        assert f"WARNING ('{pathbad}',): invalid json" in cap.out
        assert f"WARNING ('{pathterrible}',): invalid json" in cap.out
        assert sum(1 for l in cap.out.splitlines() if 'WARNING' in l) == 2
