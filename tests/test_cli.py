from pathlib import Path
import pytest
import re
from spot_check_files import cli

def test_help(capsys):
    doc = Path('doc')
    with pytest.raises(SystemExit):
        cli.main(['-h'])
    cap = capsys.readouterr()
    doc.joinpath('usage.txt').write_text(
        re.sub(r'\S*pytest\S*', 'spot_check_files', cap.out))
