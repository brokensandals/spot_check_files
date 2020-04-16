from contextlib import contextmanager
from contextlib import nullcontext
from os import PathLike
from spot_check_files.jsoninspector import JSONInspector
from spot_check_files.zipinspector import ZipInspector


@contextmanager
def _fs_extractor(path):
    with open(path, 'rb') as file:
        yield file


class Checker:
    def __init__(self):
        self.vpaths = []
        self.problems = {}

    def inspect(self, path_or_file, vpath=None):
        if isinstance(path_or_file, (str, bytes, PathLike)):
            self._inspect((str(path_or_file),), _fs_extractor)
        elif not vpath:
            raise ValueError('vpath is required when inspecting a file-like')
        else:
            self._inspect(vpath, lambda _: nullcontext(path_or_file))

    def _inspect(self, vpath, extractor):
        self.vpaths.append(vpath)
        ic = self.inspector_class(vpath)
        if not ic:
            return
        with extractor(vpath[-1]) as file:
            with ic(file, vpath) as inspector:
                problems = inspector.problems()
                if problems:
                    self.problems[vpath] = problems
                for name in inspector.filenames():
                    self._inspect(vpath + (name,), inspector.extract)

    def inspector_class(self, vpath):
        if vpath[-1].endswith('.json'):
            return JSONInspector
        elif vpath[-1].endswith('.zip'):
            return ZipInspector
        return None
