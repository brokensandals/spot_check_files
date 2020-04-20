from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union


@dataclass
class CheckRequest:
    """Represents a file that should be checked.

    Attributes:
        path - path to the file to check
        tmpdir - a shared temporary directory
        png - if True, a png thumbnail should be generated
    """
    path: Path
    tmpdir: Path
    png: bool = False


@dataclass
class CheckResult:
    """The result of a checking a file.
    Attributes:
        errors - any problems found with the file
        extracted - if the file was an archive, the path to the directory
                    containing its extracted contents. This should be a
                    subdirectory of the tmpdir specified in the request
        identified - when False, indicates the checker was unsure if the
                     given file was of a file type that it recognizes
        png - a thumbnail of the file
    """
    errors: List[Union[str, Exception]] = field(default_factory=list)
    extracted: Path = None
    identified: bool = False
    png: bytes = None


class Checker:
    def check(self, req: CheckRequest) -> CheckResult:
        """Validate, extract, and/or make a thumbnail of the specified file.

        Errors relating to a problem with the file should be caught and added
        to the errors list of the result. Errors which may indicate a that the
        checker itself is unable to operate on valid files can be propagated.
        """
        raise NotImplementedError()
