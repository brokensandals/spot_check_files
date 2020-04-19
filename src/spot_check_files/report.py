import base64
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


class Report:
    def __init__(self, files: List[FileInfo],
                 thumbnails: List[FileInfo]):
        self.files = files
        self.thumbnails = thumbnails

        arch = [f for f in files if f.mere_container]
        self.count_arch = len(arch)
        self.size_arch = sum(f.size for f in arch)
        nonarch = [f for f in files if not f.mere_container]
        self.count_nonarch = len(nonarch)
        self.size_nonarch = sum(f.size for f in nonarch)
        rec = [f for f in nonarch if f.recognized]
        self.count_rec = len(rec)
        self.frac_rec = self.count_rec / self.count_nonarch
        self.size_rec = sum(f.size for f in rec)
        self.frac_size_rec = self.size_rec / self.size_nonarch
        # TODO: will give messed up stats if f.problems and f.mere_container
        #       really, those should be mutually exclusive
        prob = [f for f in files if f.problems]
        self.count_prob = len(prob)
        self.frac_prob = self.count_prob / self.count_nonarch
        self.size_prob = sum(f.size for f in prob)
        self.frac_size_prob = self.size_prob / self.size_nonarch
        self.count_thumb = len(thumbnails)
        self.frac_thumb = self.count_thumb / self.count_nonarch
        self.size_thumb = sum(f.size for f in thumbnails)
        self.frac_size_thumb = self.size_thumb / self.size_nonarch

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

    def html(self):
        from jinja2 import Environment, PackageLoader, select_autoescape
        env = Environment(
            loader=PackageLoader('spot_check_files', 'templates'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True)
        env.globals['b64encode'] = base64.b64encode
        template = env.get_template('report.html')
        return template.render(vars(self))
