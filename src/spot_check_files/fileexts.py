from __future__ import annotations
from typing import Dict
from spot_check_files.archives import TarChecker, ZipChecker
from spot_check_files.checker import Checker, CheckResult, CheckRequest


class FileExtChecker(Checker):
    """Selects and runs a Checker based on a file's extension.

    If the Checker matching the file extension does not recognize the file,
    this Checker will mark itself as the recognizer and add an error.

    Attributes:
        checkers - map of file extensions (e.g. "tar.gz") to the Checker
                   to use for those files
    """

    @classmethod
    def default(cls) -> FileExtChecker:
        """Returns an instance configured for some standard file types."""
        ctar = TarChecker()
        czip = ZipChecker()
        checkers = {
            'tar': ctar,
            'tar.bz2': ctar,
            'tar.gz': ctar,
            'tar.xz': ctar,
            'tbz': ctar,
            'tgz': ctar,
            'txz': ctar,
            'zip': czip,
        }
        return cls(checkers)

    def __init__(self, checkers: Dict[str, Checker] = {}):
        self.checkers = dict(checkers)

    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        parts = req.path.name.lower().split('.')
        parts.pop(0)
        while len(parts) > 1:
            ext = '.'.join(parts)
            checker = self.checkers.get(ext, None)
            if checker:
                result = checker.check(req)
                if result.recognizer is None:
                    result.recognizer = self
                    result.errors.append(
                        f'expected to be recognized by {checker} based '
                        'on file extension')
                break
            parts.pop(0)
        return result
