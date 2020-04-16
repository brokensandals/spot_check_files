from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from spot_check_files.base import\
    BodyCallback, ChildCallback, FileInfo, Inspector


class QLInspector(Inspector):
    def name(self):
        return 'quicklook'

    def inspect(self, info: FileInfo, get_data: BodyCallback, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        if not thumbnail:
            return

        with get_data() as data:
            filename = Path(info.pathseq[-1]).name
            with TemporaryDirectory() as tmpdir:
                tmpdirpath = Path(tmpdir)
                dest = tmpdirpath.joinpath(filename)
                with dest.open('wb') as out:
                    shutil.copyfileobj(data, out)
                subprocess.check_output(
                    ['qlmanage', '-t', '-s', '512', str(dest), '-o', tmpdir])
                for path in tmpdirpath.glob('*.png'):
                    info.thumbnail = path.read_bytes()
                    info.recognized = True
                    return
