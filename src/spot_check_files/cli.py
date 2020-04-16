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


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path', nargs='+',
        help='files or folders to check')
    args = parser.parse_args(args)

    checker = Checker()
    for path in args.path:
        checker.check(path)

    print(f'Total files: {len(checker.vpaths)}')
    for vpath in checker.problems:
        for problem in checker.problems[vpath]:
            print(f'WARNING {vpath}: {problem}')

    if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
        _print_images(checker)

    return 0
