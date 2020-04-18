import os
from typing import List
from spot_check_files.base import FileInfo


def _total_size(fileinfos):
    return sum(f.size for f in fileinfos)


def _print_images(fileinfos):
    try:
        from imgcat import imgcat
    except ImportError:
        return

    for file in fileinfos:
        print()
        print(f'thumbnail for {file.pathseq}:')
        imgcat(file.thumbnail)


def _fractions(subset, fullset):
    return (len(subset) / len(fullset),
            _total_size(subset) / _total_size(fullset))


class Report:
    def __init__(self, files: List[FileInfo],
                 thumbnails: List[FileInfo]):
        self.files = files
        self.thumbnails = thumbnails

        self.count_arch = sum(1 for f in files if f.mere_container)
        nonarch = [f for f in files if not f.mere_container]
        self.count_nonarch = len(nonarch)
        self.size_nonarch = sum(f.size for f in nonarch)
        rec = [f for f in nonarch if f.recognized]
        count_rec = len(rec)
        self.frac_rec = count_rec / self.count_nonarch
        size_rec = sum(f.size for f in rec)
        self.frac_size_rec = size_rec / self.size_nonarch
        count_thumb = len(thumbnails)
        self.frac_thumb = count_thumb / self.count_nonarch
        size_thumb = sum(f.size for f in thumbnails)
        self.frac_size_thumb = size_thumb / self.size_nonarch

    def print(self):
        print(f'Archives: {self.count_arch}')
        print(f'Leaf files: {self.count_nonarch}, {self.size_nonarch} bytes')
        print('Recognized {:.0%} of files, {:.0%} by size'
              .format(self.frac_rec, self.frac_size_rec))
        print('Made thumbnails of {:.0%} of files, {:.0%} by size'
              .format(self.frac_thumb, self.frac_size_thumb))

        for file in self.files:
            for problem in file.problems:
                print(f'WARNING {file.pathseq}: {problem}')

        if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
            _print_images(self.thumbnails)
