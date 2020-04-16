from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory


class QLInspector:
    def __init__(self, file, vpath):
        self.file = file
        self.filename = Path(vpath[-1]).name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def filenames(self):
        return []

    def problems(self):
        return []

    def thumbnail(self):
        with TemporaryDirectory() as tmpdir:
            tmpdirpath = Path(tmpdir)
            dest = tmpdirpath.joinpath(self.filename)
            with dest.open('wb') as out:
                shutil.copyfileobj(self.file, out)
            subprocess.check_call(
                ['qlmanage', '-t', '-s', '512', str(dest), '-o', tmpdir])
            for path in tmpdirpath.glob('*.png'):
                return path.read_bytes()
            return None
