from pathlib import Path
from os import PathLike
import platform
import random
import re
from typing import List, Pattern, Tuple
from spot_check_files.base import FileAccessor, FileInfo, FSFileAccessor,\
    Inspector
from spot_check_files.jsoninspector import JSONInspector
from spot_check_files.qlinspector import QLInspector
from spot_check_files.tarinspector import ExtractingTarInspector,\
    StreamingTarInspector
from spot_check_files.xmlinspector import XMLInspector
from spot_check_files.zipinspector import ExtractingZipInspector,\
    StreamingZipInspector


def default_inspectors(streaming=False):
    inspectors = []
    inspectors.append((r'.*\.json\Z', JSONInspector()))
    inspectors.append((r'.*\.xml\Z', XMLInspector()))
    tar_regex = r'.*\.(tar\.(gz|bz2|xz)|tgz|tbz|txz)\Z'
    if streaming:
        inspectors.append((r'.*\.zip\Z', StreamingZipInspector()))
        inspectors.append((tar_regex, StreamingTarInspector()))
    else:
        inspectors.append((r'.*\.zip\Z', ExtractingZipInspector()))
        inspectors.append((tar_regex, ExtractingTarInspector()))
    if platform.mac_ver()[0]:
        inspectors.append((r'.*', QLInspector()))
    return inspectors


class Checker:
    files: List[FileInfo]
    num_thumbnails: int
    thumbnail_files: List[FileInfo]
    inspectors: List[Tuple[Pattern, Inspector]]

    def __init__(self, *, num_thumbnails: int = 3,
                 inspectors: List[Tuple[Pattern, Inspector]] = None):
        self.files = []
        self.num_thumbnails = num_thumbnails
        self.thumbnail_files = []
        self.inspectors = inspectors or default_inspectors()

    def check_path(self, path: PathLike):
        path = Path(path)
        if path.is_file():
            size = path.stat().st_size
            info = FileInfo(pathseq=(str(path),), size=size)
            self.check(info, FSFileAccessor(path))
        elif path.is_dir():
            for child in path.glob('**/*'):
                if child.is_file():
                    self.check_path(child)
        else:
            raise ValueError(f'no file or folder at path: {path}')

    def check(self, info: FileInfo, accessor: FileAccessor):
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
            inspector.inspect(info, accessor,
                              thumbnail=thumbnail, on_child=self.check)
            if thumbnail and info.thumbnail:
                if len(self.thumbnail_files) < self.num_thumbnails:
                    self.thumbnail_files.append(info)
                else:
                    self.thumbnail_files[tnindex] = info

    def inspector(self, info: FileInfo):
        for (pattern, inspector) in self.inspectors:
            if re.match(pattern, info.pathseq[-1], re.IGNORECASE):
                return inspector
        return None
