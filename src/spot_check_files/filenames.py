from __future__ import annotations
import fnmatch
from typing import List, Tuple
from spot_check_files.archives import TarChecker, ZipChecker
from spot_check_files.basics import CSVChecker, PlaintextChecker
from spot_check_files.checker import Checker, CheckResult, CheckRequest


class FileNameChecker(Checker):
    """Selects and runs a Checker based on a file's (logical) path.

    If the Checker matching the filename does not recognize the file,
    this Checker will mark itself as the recognizer and add an error.

    The virtpath attribute of the CheckRequest is used.

    Attributes:
        checkers - list of tuples mapping filename pattern
                   (as specified in fnmatch module) to Checker
    """

    @classmethod
    def default(cls) -> FileNameChecker:
        """Returns an instance configured for some standard file types."""
        ctar = TarChecker()
        checkers = [
            ('*.csv', CSVChecker()),
            ('*.tar', ctar),
            ('*.tar.bz2', ctar),
            ('*.tar.gz', ctar),
            ('*.tar.xz', ctar),
            ('*.tbz', ctar),
            ('*.tgz', ctar),
            ('*.txt', PlaintextChecker()),
            ('*.txz', ctar),
            ('*.zip', ZipChecker()),
        ]
        return cls(checkers)

    def __init__(self, checkers: List[Tuple[str, Checker]] = []):
        self.checkers = list(checkers)

    def check(self, req: CheckRequest) -> CheckResult:
        for (pattern, checker) in self.checkers:
            if fnmatch.fnmatch(str(req.virtpath), pattern):
                result = checker.check(req)
                if result.recognizer is None:
                    result.recognizer = self
                    result.errors.append(
                        f'expected to be recognized by {checker} because '
                        f'filename matched: {pattern}')
                return result
        return CheckResult()
