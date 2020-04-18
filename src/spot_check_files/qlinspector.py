from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from spot_check_files.base import\
    ChildCallback, FileAccessor, FileInfo, Inspector


class QLInspector(Inspector):
    thumbnails_only: bool

    def __init__(self, thumbnails_only: bool = False):
        self.thumbnails_only = thumbnails_only

    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        if not thumbnail and self.thumbnails_only:
            return
        with accessor.path() as path:
            with TemporaryDirectory() as tmpdir:
                tmpdirpath = Path(tmpdir)
                subprocess.check_output(
                    ['qlmanage', '-t', '-s', '512', str(path), '-o', tmpdir])
                for outpath in tmpdirpath.glob('*.png'):
                    if thumbnail:
                        info.thumbnail = outpath.read_bytes()
                    info.recognized = True
                    return
