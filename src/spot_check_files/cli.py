import argparse
import os
from spot_check_files.checker import Checker, default_inspectors


def _print_images(fileinfos):
    try:
        from imgcat import imgcat
    except ImportError:
        return

    for file in fileinfos:
        print(f'thumbnail for {file.pathseq}:')
        imgcat(file.thumbnail)
        print()


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
    parser.set_defaults(thumbnails=[3], streaming=False)
    args = parser.parse_args(args)

    inspectors = default_inspectors(streaming=args.streaming)
    checker = Checker(
        num_thumbnails=args.thumbnails[0],
        inspectors=inspectors)

    for path in args.path:
        checker.check_path(path)

    print(f'Total files: {len(checker.files)}')
    for file in checker.files:
        for problem in file.problems:
            print(f'WARNING {file.pathseq}: {problem}')

    if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
        _print_images(checker.thumbnail_files)

    return 0
