import argparse
import os
from spot_check_files.checker import Checker


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
        '-t', '--thumbnails', nargs='?', type=int,
        help='maximum number of thumbnails to generate')
    parser.set_defaults(thumbnails=3)
    args = parser.parse_args(args)

    checker = Checker(num_thumbnails=args.thumbnails)
    for path in args.path:
        checker.check_path(path)

    print(f'Total files: {len(checker.files)}')
    for file in checker.files:
        for problem in file.problems:
            print(f'WARNING {file.pathseq}: {problem}')
    print()

    if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
        _print_images(checker.thumbnail_files)

    return 0
