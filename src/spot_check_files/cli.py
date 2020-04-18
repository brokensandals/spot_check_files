import argparse
import platform
from spot_check_files.checker import Checker, default_inspectors
from spot_check_files.qlinspector import QLInspector
from spot_check_files.report import Report


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path', nargs='+',
        help='files or folders to check')
    parser.add_argument(
        '-t', '--thumbnails', nargs=1, type=int,
        help='maximum number of thumbnails to generate')
    parser.add_argument(
        '-s', '--streaming', action='store_true',
        help='avoid extracting files to disk when possible')
    parser.add_argument(
        '-q', '--quicklook',
        choices=['off', 'thumbnails', 'checks', 'auto'],
        default='auto',
        help='Whether to use OS X\'s Quick Look on files. '
             'Quick Look can enable recognizing far more file types, but '
             'invoking it is slow. '
             '"off" means never use it. '
             '"thumbnails" means only use it when generating a thumbnail.'
             '"checks" means invoke it for all unrecognized files.'
             '"auto" means "checks" on OS X, otherwise "off".'
    )
    parser.set_defaults(thumbnails=[3], streaming=False)
    args = parser.parse_args(args)

    inspectors = default_inspectors(streaming=args.streaming)
    if (args.quicklook == 'auto' and platform.mac_ver()[0])\
       or args.quicklook != 'off':
        inspectors.append((r'.*',
                           QLInspector(args.quicklook == 'thumbnails')))
    checker = Checker(
        num_thumbnails=args.thumbnails[0],
        inspectors=inspectors)

    for path in args.path:
        checker.check_path(path)

    report = Report(checker.files, checker.thumbnail_files)
    report.print()

    return 0
