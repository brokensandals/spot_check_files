from __future__ import annotations
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
from io import IOBase
from os import PathLike
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import Callable, ContextManager, List, Tuple, Union


PathSeq = Tuple[str, ...]


@dataclass
class FileInfo:
    pathseq: PathSeq
    size: int
    inspector: Inspector = None
    mere_container: bool = False
    problems: List[str] = field(default_factory=list)
    recognized: bool = False
    thumbnail: bytes = None


class FileAccessor:
    def path(self) -> ContextManager[Path]:
        raise NotImplementedError()

    def io(self) -> ContextManager[IOBase]:
        raise NotImplementedError()

    def agnostic(self) -> Union[ContextManager[Path], ContextManager[IOBase]]:
        raise NotImplementedError()


class FSFileAccessor(FileAccessor):
    def __init__(self, path: PathLike):
        self._path = Path(path)
        self.agnostic = self.path

    def path(self) -> ContextManager[Path]:
        return nullcontext(self._path)

    def io(self) -> ContextManager[Path]:
        return open(self._path, 'rb')


class IOFileAccessor(FileAccessor):
    def __init__(self, pathseq: PathSeq,
                 iofunc: Callable[[], ContextManager[IOBase]]):
        self.io = iofunc
        self.filename = Path(pathseq[-1]).name
        self.agnostic = self.io

    @contextmanager
    def path(self):
        with self.io() as data:
            with TemporaryDirectory() as tmpdir:
                path = Path(tmpdir).joinpath(self.filename)
                with path.open('wb') as out:
                    shutil.copyfileobj(data, out)
                yield path


ChildCallback = Callable[[FileInfo, FileAccessor], None]


class Inspector:
    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        raise NotImplementedError()
