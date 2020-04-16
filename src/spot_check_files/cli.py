import argparse
from spot_check_files.checker import Checker


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

    return 0
