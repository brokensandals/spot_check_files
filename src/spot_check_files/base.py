from __future__ import annotations
from dataclasses import dataclass, field
from io import IOBase
from typing import Callable, ContextManager, List, Tuple


@dataclass
class FileInfo:
    pathseq: Tuple[str, ...]
    size: int
    inspector: Inspector = None
    mere_container: bool = False
    problems: List[str] = field(default_factory=list)
    recognized: bool = False
    thumbnail: bytes = None


BodyCallback = Callable[[], ContextManager[IOBase]]
ChildCallback = Callable[[FileInfo, BodyCallback], None]


class Inspector:
    def name(self):
        raise NotImplementedError()

    def inspect(self, info: FileInfo, get_data: BodyCallback, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        raise NotImplementedError()
