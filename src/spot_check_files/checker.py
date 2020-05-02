"""Defines the API for file checkers and a helper class for running them.

The Checker abstract class defines the interface that must be implemented
for each type of file that spotcheck will support. A Checker is given a
CheckRequest containing the path to a file and other info, and returns a
CheckResult indicating whether it knew how to interpret the file, any errors
it found in the file, and a thumbnail of the file. The Checker also extracts
files if the file is an archive (e.g. a zip or tar).

The CheckerRunner class recursively checks all the files in a given path
(including files inside archives, if it's configured with a Checker that
can extract the archive) using a given set of Checkers.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from PIL import Image
from pathlib import Path
import platform
from tempfile import TemporaryDirectory
from typing import List, Union


@dataclass
class CheckRequest:
    """Represents a file that should be checked.

    Attributes:
        realpath - path to (possibly temporary) location of file
        tmpdir - a shared temporary directory
        virtpath - logical path associated with the file. For example,
                   if the file "foo/bar.txt" was extracted from "a.zip",
                   this might be "a.zip/foo/bar.txt".
        thumb - if True, a thumbnail should be generated
    """
    realpath: Path
    tmpdir: Path
    virtpath: Path
    thumb: bool = False


@dataclass
class CheckResult:
    """The result of a checking a file.
    Attributes:
        errors - any problems found with the file
        extracted - if the file was an archive, the path to the directory
                    containing its extracted contents. This should be a
                    subdirectory of the tmpdir specified in the request
        recognizer - a Checker will set this to itself if it's confident
                     that the file was valid or invalid; if the file type
                     is still unclear, this may be None
        skipped - if True, the Checker decided this file should not be
                  checked. recognizer should always be set when this is True.
        thumb - a thumbnail of the file
    """
    errors: List[Union[str, Exception]] = field(default_factory=list)
    extracted: Path = None
    thumb: Image = None
    recognizer: Checker = None
    skipped: bool = False


class Checker:
    def check(self, req: CheckRequest) -> CheckResult:
        """Validate, extract, and/or make a thumbnail of the specified file.

        Errors relating to a problem with the file should be caught and added
        to the errors list of the result. Errors which may indicate a that the
        checker itself is unable to operate on valid files can be propagated.
        """
        raise NotImplementedError()


@dataclass
class FileSummary:
    """Records metadata about a file, and the result of checking it.

    Attributes:
        result - result from the first checker that recognized the file,
                 or an empty result
        size - size in bytes of the file
        virtpath - the logical path to the file (for files inside an archive,
                   this wil include the path to the archive)
    """
    size: int
    virtpath: Path
    result: CheckResult = field(default_factory=CheckResult)


class CheckerRunner:
    """This is the main entry point for spot-checking files.

    What types of files will be checked, and how they will be recognized,
    is determined by the checkers attribute. The CheckerRunner.default()
    method will create an instance with a default set of checkers.

    The check_path method should be called for each file or directory you
    wish to check.

    Attributes:
        checkers - for each file, these will be applied in order until
                    one recognizes the file
    """
    @classmethod
    def default(cls):
        """Returns an instance with hopefully-reasonable defaults.

        Default checkers, in order:
            1. FileNameChecker.default()
            2. If on a Mac, QlChecker
        """
        from spot_check_files.filenames import FileNameChecker
        checkers = [FileNameChecker.default()]
        if platform.mac_ver()[0]:
            from spot_check_files.quicklook import QLChecker
            checkers.append(QLChecker())
        return cls(checkers)

    def __init__(self, checkers: List[Checker] = []):
        self.checkers = list(checkers)

    def check_path(self, path: Path, virtpath: Path = None,
                   tmpdir: Path = None) -> List[FileSummary]:
        """Runs checks against the file or directory at the given path."""
        if not tmpdir:
            with TemporaryDirectory() as tmpdir:
                return self.check_path(path, virtpath, Path(tmpdir))
        results = []
        virtpath = virtpath or path
        if path.is_dir():
            for fpath in path.glob('**/*'):
                if fpath.is_file():
                    fvirtpath = virtpath.joinpath(fpath.relative_to(path))
                    results.extend(self.check_path(fpath, fvirtpath, tmpdir))
            return results
        elif path.is_file():
            summary = FileSummary(
                virtpath=virtpath,
                size=path.stat().st_size)
            results.append(summary)
            for checker in self.checkers:
                req = CheckRequest(
                    realpath=path, tmpdir=tmpdir, virtpath=virtpath,
                    thumb=True)
                res = checker.check(req)
                if res.recognizer:
                    summary.result = res
                    if res.extracted:
                        results.extend(
                            self.check_path(res.extracted, virtpath, tmpdir))
                    break
        return results
