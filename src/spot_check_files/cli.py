import argparse
from pathlib import Path
from spot_check_files.checker import CheckerRunner
from spot_check_files.report import CheckReport


def main(args=None):
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
