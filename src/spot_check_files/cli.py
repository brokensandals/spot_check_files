import argparse
import os
import platform
from spot_check_files.checker import Checker, default_inspectors
from spot_check_files.qlinspector import QLInspector


def _print_images(fileinfos):
    try:
        from imgcat import imgcat
    except ImportError:
        return

    for file in fileinfos:
        print()
        print(f'thumbnail for {file.pathseq}:')
        imgcat(file.thumbnail)


def _total_size(fileinfos):
    return sum(f.size for f in fileinfos)


def _fractions(subset, fullset):
    return (len(subset) / len(fullset),
            _total_size(subset) / _total_size(fullset))


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

    fis = [f for f in checker.files if not f.mere_container]
    rec_fis = [f for f in fis if f.recognized]
    thumb_fis = checker.thumbnail_files
    rec_fracs = _fractions(rec_fis, fis)
    thumb_fracs = _fractions(thumb_fis, fis)

    print(f'Total files: {len(checker.files)}')
    print('Recognized {:.0%} of files, {:.0%} by size'
          .format(rec_fracs[0], rec_fracs[1]))
    print('Made thumbnails of {:.0%} of files, {:.0%} by size'
          .format(thumb_fracs[0], thumb_fracs[1]))


    for file in checker.files:
        for problem in file.problems:
            print(f'WARNING {file.pathseq}: {problem}')

    if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
        _print_images(checker.thumbnail_files)

    return 0
