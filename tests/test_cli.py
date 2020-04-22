from pathlib import Path
import pytest
import re
from spot_check_files import cli


def test_help(capsys):
    with pytest.raises(SystemExit):
        cli.main(['-h'])
    cap = capsys.readouterr()
    out = re.sub(r'\S*pytest\S*', 'spotcheck', cap.out)
    Path('doc').joinpath('usage.txt').write_text(out)
