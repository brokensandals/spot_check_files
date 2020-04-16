import argparse
import os
from spot_check_files.checker import Checker


def _print_images(checker):
    try:
        from imgcat import imgcat
    except ImportError:
        return

    for (vpath, thumbnail) in checker.thumbnails:
        print(f'thumbnail for {vpath}:')
        imgcat(thumbnail)
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
        checker.check(path)

    print(f'Total files: {len(checker.vpaths)}')
    for vpath in checker.problems:
        for problem in checker.problems[vpath]:
            print(f'WARNING {vpath}: {problem}')
    print()

    if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
        _print_images(checker)

    return 0
