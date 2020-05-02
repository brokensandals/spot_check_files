"""Logic for selecting a Checker based on filenames (e.g. file extension)."""
from __future__ import annotations
import fnmatch
from typing import List, Tuple
from spot_check_files.archives import TarChecker, ZipChecker
from spot_check_files.basics import CSVChecker, ImageChecker,\
    JSONChecker, PlaintextChecker, XMLChecker
from spot_check_files.checker import Checker, CheckResult, CheckRequest


class FileNameChecker(Checker):
    """Selects and runs a Checker based on a file's (logical) path.

    If the Checker matching the filename does not recognize the file,
    this Checker will mark itself as the recognizer and add an error.

    The virtpath attribute of the CheckRequest is used.

    Attributes:
        blacklist - list of filename patterns (as specified in fnmatch
                    module) to mark as skipped
        checkers - list of tuples mapping filename pattern
                   (as specified in fnmatch module) to Checker
    """

    @classmethod
    def default(cls) -> FileNameChecker:
        """Returns an instance configured for some standard file types."""
        ctar = TarChecker()
        checkers = [
            ('*.csv', CSVChecker()),
            ('*.json', JSONChecker()),
            ('*.md', PlaintextChecker()),
            ('*.tar', ctar),
            ('*.tar.bz2', ctar),
            ('*.tar.gz', ctar),
            ('*.tar.xz', ctar),
            ('*.tbz', ctar),
            ('*.tgz', ctar),
            ('*.txt', PlaintextChecker()),
            ('*.txz', ctar),
            ('*.xml', XMLChecker()),
            ('*.zip', ZipChecker()),
        ]

        # I haven't tested most of these, they're just some of the ones
        # that Pillow supports that seem most likely to be of use to me
        img_exts = [
            'bmp',
            'gif',
            'icns',
            'ico',
            'jpg',
            'jpeg',
            'png',
            'tiff',
            'webp',
        ]
        cimg = ImageChecker()
        checkers.extend((f'*.{ext}', cimg) for ext in img_exts)

        return cls(checkers)

    def __str__(self):
        # TODO it's bad that this doesn't include any details about
        #      the instance. Possibly I shouldn't be using __str__
        #      in the reports, so that there would be less pressure
        #      for this to be short/readable. Ideally even the report
        #      would print some way of distinguishing instances, though.
        return 'FileNameChecker'

    def __init__(self, checkers: List[Tuple[str, Checker]] = [],
                 blacklist=[]):
        self.blacklist = list(blacklist)
        self.checkers = list(checkers)

    def check(self, req: CheckRequest) -> CheckResult:
        vpstr = str(req.virtpath)
        for pattern in self.blacklist:
            if fnmatch.fnmatch(vpstr, pattern):
                return CheckResult(recognizer=self,
                                   skipped=True)
        for (pattern, checker) in self.checkers:
            if fnmatch.fnmatch(vpstr, pattern):
                result = checker.check(req)
                if result.recognizer is None:
                    result.recognizer = self
                    result.errors.append(
                        f'expected to be recognized by {checker} because '
                        f'filename matched: {pattern}')
                return result
        return CheckResult()
