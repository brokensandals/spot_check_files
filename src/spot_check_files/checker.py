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
        self.problems = {}
        self.vpaths = []

    def check(self, path_or_file, vpath=None):
        if isinstance(path_or_file, (str, bytes, PathLike)):
            self._check((str(path_or_file),), _fs_extractor)
        elif not vpath:
            raise ValueError('vpath is required when inspecting a file-like')
        else:
            self._check(vpath, lambda _: nullcontext(path_or_file))

    def _check(self, vpath, extractor):
        ic = self.inspector_class(vpath)
        if not ic:
            self.visit(vpath, None)
            return
        with extractor(vpath[-1]) as file:
            with ic(file, vpath) as inspector:
                self.visit(vpath, inspector)
                for name in inspector.filenames():
                    self._check(vpath + (name,), inspector.extract)

    def visit(self, vpath, inspector):
        self.vpaths.append(vpath)
        if inspector:
            problems = inspector.problems()
            if problems:
                self.problems[vpath] = problems

    def inspector_class(self, vpath):
        if vpath[-1].endswith('.json'):
            return JSONInspector
        elif vpath[-1].endswith('.zip'):
            return ZipInspector
        return None
