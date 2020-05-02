"""Handles summarizing and formatting results. Main class is CheckReport."""
import base64
from io import BytesIO
import os
from PIL import Image
from terminaltables import AsciiTable
from typing import List
from spot_check_files.checker import FileSummary


def _print_thumbs(summaries):
    try:
        from imgcat import imgcat
    except ImportError:
        return

    while summaries:
        # Combine images to show three per line in the output
        group = [s.result.thumb for s in summaries[0:3]]
        boxes = [i.getbbox() for i in group]
        if any(boxes):
            width = sum(b[2] - b[0] + 1 for b in boxes if b)
            height = max(b[3] - b[1] + 1 for b in boxes if b)
            img = Image.new('RGBA', (width, height))
            x = 0
            for i in range(len(group)):
                if boxes[i] is None:
                    continue
                img.paste(group[i], (x, 0))
                x += boxes[i][2] - boxes[i][0] + 1
            imgcat(img)
        summaries = summaries[3:]


class _GroupStats:
    def __init__(self, name: str, summaries: List[FileSummary],
                 comparison: List[FileSummary] = None):
        self.name = name
        self.count = len(summaries)
        self.size = sum(s.size for s in summaries)
        self.count_pct = ''
        self.size_pct = ''
        if comparison:
            self.count_pct = '{:.0%}'.format(self.count / len(comparison))
            self.size_pct = '{:.0%}'.format(
                self.size / sum(s.size for s in comparison))


class CheckReport:
    """Formats and displays results from a CheckerRunner."""
    def __init__(self, summaries: List[FileSummary]):
        self.summaries = summaries
        arch_summaries = [s for s in summaries
                          if s.result.extracted
                          and not s.result.errors]
        leaf_summaries = [s for s in summaries
                          if s.result.errors or not s.result.extracted]
        skip_summaries = [s for s in leaf_summaries if s.result.skipped]
        # If we ever get something that was extracted then marked as skipped,
        # a Checker is misusing the Checker API.
        # TODO: enforce this better, somewhere else
        assert not [s for s in arch_summaries if s.result.skipped]
        self.err_summaries = [s for s in leaf_summaries if s.result.errors]
        self.thumb_summaries = [s for s in leaf_summaries if s.result.thumb]
        self.groups = [
            _GroupStats('Archives (without errors)', arch_summaries),
            _GroupStats('Files (excludes errorless archives)',
                        leaf_summaries),
            _GroupStats('Skipped files', skip_summaries, leaf_summaries),
            _GroupStats('Files with thumbnails', self.thumb_summaries,
                        leaf_summaries),
            _GroupStats('Files with ERRORS', self.err_summaries,
                        leaf_summaries),
        ]

        by_rec = {}
        unrec_by_ext = {}
        for summary in leaf_summaries:
            if summary.result.recognizer is None:
                ext = summary.virtpath.suffix
                if ext not in unrec_by_ext:
                    unrec_by_ext[ext] = []
                unrec_by_ext[ext].append(summary)
            else:
                rec = str(summary.result.recognizer)
                if rec not in by_rec:
                    by_rec[rec] = []
                by_rec[rec].append(summary)

        for rec in sorted(by_rec.keys()):
            self.groups.append(_GroupStats(f'Recognized by {rec}',
                                           by_rec[rec], leaf_summaries))

        for ext in sorted(unrec_by_ext.keys()):
            if not ext:
                continue
            self.groups.append(_GroupStats(
                f'Unrecognized with extension {ext}',
                unrec_by_ext[ext], leaf_summaries))
        if '' in unrec_by_ext:
            self.groups.append(_GroupStats(
                'Other unrecognized', unrec_by_ext[''], leaf_summaries))

    def print(self):
        """Prints the report to the terminal.

        If using iTerm2, thumbnails are displayed; otherwise, they are
        not used.
        """
        if os.environ.get('TERM_PROGRAM', None) == 'iTerm.app':
            _print_thumbs(self.thumb_summaries)

        for summary in self.err_summaries:
            print(f'ERRORS for {summary.virtpath}')
            for err in summary.result.errors:
                print(f'\t{err}')
            print()

        stats = [('Group', 'Files', 'Size', '% Files', '% Size')]
        stats.extend((g.name,
                      g.count,
                      g.size,
                      g.count_pct,
                      g.size_pct) for g in self.groups)
        table = AsciiTable(stats)
        for i in range(1, 5):
            table.justify_columns[i] = 'right'
        print(table.table)

    def html(self) -> str:
        """Returns an HTML version of the report, as a string."""
        from jinja2 import Environment, PackageLoader, select_autoescape

        def thumburl(summary):
            data = BytesIO()
            summary.result.thumb.save(data, 'png')
            encdata = base64.b64encode(data.getvalue()).decode('utf-8')
            return f'data:image/png;base64,{encdata}'

        env = Environment(
            loader=PackageLoader('spot_check_files', '_templates'),
            autoescape=select_autoescape(['html']),
            trim_blocks=True)
        env.globals['thumburl'] = thumburl
        template = env.get_template('report.html')
        return template.render(vars(self))
