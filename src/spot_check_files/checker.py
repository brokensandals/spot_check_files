from contextlib import contextmanager
from contextlib import nullcontext
from pathlib import Path
from os import PathLike
import platform
import random
from spot_check_files.base import BodyCallback, FileInfo
from spot_check_files.jsoninspector import JSONInspector
from spot_check_files.qlinspector import QLInspector
from spot_check_files.zipinspector import ZipInspector


class Checker:
    def __init__(self, *, num_thumbnails=3):
        self.files = []
        self.num_thumbnails = num_thumbnails
        self.thumbnail_files = []

    def check_path(self, path: PathLike):
        path = Path(path)
        if path.is_file():
            size = path.stat().st_size
            info = FileInfo(pathseq=(str(path),), size=size)
            self.check(info, lambda: path.open('rb'))
        elif path.is_dir():
            for child in path.glob('**/*'):
                if child.is_file():
                    self.check_path(child)
        else:
            raise ValueError(f'no file or folder at path: {path}')

    def check(self, info: FileInfo, get_data: BodyCallback):
        self.files.append(info)
        inspector = self.inspector(info)
        if inspector:
            info.inspector = inspector
            tnindex = 0
            if self.num_thumbnails:
                if len(self.thumbnail_files) < self.num_thumbnails:
                    tnindex = len(self.thumbnail_files)
                else:
                    tnindex = random.randrange(0, len(self.files))
            thumbnail = tnindex < self.num_thumbnails
            inspector.inspect(info, get_data,
                              thumbnail=thumbnail, on_child=self.check)
            if thumbnail and info.thumbnail:
                if len(self.thumbnail_files) < self.num_thumbnails:
                    self.thumbnail_files.append(info)
                else:
                    self.thumbnail_files[tnindex] = info

    def inspector(self, info: FileInfo):
        if info.pathseq[-1].lower().endswith('.zip'):
            return ZipInspector()
        if info.pathseq[-1].lower().endswith('.json'):
            return JSONInspector()
        if platform.mac_ver()[0]:
            return QLInspector()
        return None
