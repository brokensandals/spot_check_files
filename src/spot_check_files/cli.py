"""Implements the spotcheck command-line tool."""
import argparse
from pathlib import Path
from typing import List
from spot_check_files.checker import CheckerRunner
from spot_check_files.report import CheckReport


def main(args: List[str] = None) -> int:
    """Checks one or more paths and displays the output.

    See docs/usage.txt for usage.

    If args is omitted, the process's command-line args are used.

    Returns 0 to indicate success.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='+', help='file or folders to check')
    parser.add_argument('-H', '--html', action='store_true', default=False,
                        help='output HTML')
    args = parser.parse_args(args)
    runner = CheckerRunner.default()
    summaries = []
    for path in args.path:
        summaries.extend(runner.check_path(Path(path)))
    report = CheckReport(summaries)
    if args.html:
        print(report.html())
    else:
        report.print()
    return 0
