from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from spot_check_files.base import\
    ChildCallback, FileAccessor, FileInfo, Inspector


class QLInspector(Inspector):
    def name(self):
        return 'quicklook'

    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        if not thumbnail:
            return

        with accessor.path() as path:
            with TemporaryDirectory() as tmpdir:
                tmpdirpath = Path(tmpdir)
                subprocess.check_output(
                    ['qlmanage', '-t', '-s', '512', str(path), '-o', tmpdir])
                for outpath in tmpdirpath.glob('*.png'):
                    info.thumbnail = outpath.read_bytes()
                    info.recognized = True
                    return
