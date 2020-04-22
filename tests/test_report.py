from pathlib import Path
from PIL import Image
import re
from spot_check_files.archives import ZipChecker
from spot_check_files.basics import CSVChecker, ImageChecker, PlaintextChecker
from spot_check_files.checker import CheckResult, FileSummary
from spot_check_files.quicklook import QLChecker
from spot_check_files.report import CheckReport


_HTMLDIR = Path('tmp')


def setup_module(module):
    _HTMLDIR.mkdir(exist_ok=True)


def test_empty(capsys):
    report = CheckReport([])
    report.print()
    cap = capsys.readouterr()
    assert re.search(r'^.*Files[^1-9]*$', cap.out, re.MULTILINE)
    html = report.html()
    _HTMLDIR.joinpath('empty.html').write_text(html)


def test_errors(capsys):
    s1 = FileSummary(
        size=15, virtpath=Path('alpha/file1.txt'),
        result=CheckResult(
            recognizer=PlaintextChecker(),
            errors=['really unpleasant file',
                    'did not care for it']))
    s2 = FileSummary(
        size=23, virtpath=Path('alpha/file2.txt'),
        result=CheckResult(
            recognizer=PlaintextChecker(),
            errors=[ValueError('bad')]))
    s3 = FileSummary(
        size=39, virtpath=Path('alpha/file3.txt'),
        result=CheckResult(recognizer=PlaintextChecker()))
    report = CheckReport([s1, s2, s3])
    groups = [g for g in report.groups if g.name == 'Files with ERRORS']
    assert len(groups) == 1
    assert groups[0].count == 2
    assert groups[0].size == 38
    assert groups[0].count_pct == '67%'
    assert groups[0].size_pct == '49%'
    assert report.err_summaries == [s1, s2]
    report.print()
    cap = capsys.readouterr()
    assert re.search(r'^.*Files with ERRORS.*2.*$', cap.out, re.MULTILINE)
    assert ('ERRORS for alpha/file1.txt\n'
            '\treally unpleasant file\n'
            '\tdid not care for it\n' in cap.out)
    assert 'ERRORS for alpha/file2.txt\n\tbad\n' in cap.out
    html = report.html()
    _HTMLDIR.joinpath('errors.html').write_text(html)


def test_archives(capsys):
    s1 = FileSummary(
        size=15, virtpath=Path('good.zip'),
        result=CheckResult(recognizer=ZipChecker(), extracted=Path('moot')))
    s2 = FileSummary(
        size=23, virtpath=Path('bad.zip'),
        result=CheckResult(
            recognizer=ZipChecker(),
            extracted=Path('moot'),
            errors=['wut']))
    s3 = FileSummary(
        size=39, virtpath=Path('other.txt'),
        result=CheckResult(recognizer=PlaintextChecker()))
    report = CheckReport([s1, s2, s3])
    errgroups = [g for g in report.groups if g.name == 'Files with ERRORS']
    assert len(errgroups) == 1
    assert errgroups[0].count == 1
    assert errgroups[0].size == 23
    assert errgroups[0].count_pct == '50%'
    assert errgroups[0].size_pct == '37%'  # s2.size / (s2.size + s3.size)
    assert report.err_summaries == [s2]
    arcgroups = [g for g in report.groups if 'Archives' in g.name]
    assert len(arcgroups) == 1
    assert arcgroups[0].count == 1
    assert arcgroups[0].size == 15
    assert arcgroups[0].count_pct == ''
    assert arcgroups[0].size_pct == ''
    fgroups = [g for g in report.groups if 'Files (excludes' in g.name]
    assert len(fgroups) == 1
    assert fgroups[0].count == 2
    assert fgroups[0].size == 62
    assert fgroups[0].count_pct == ''
    assert fgroups[0].size_pct == ''
    report.print()
    cap = capsys.readouterr()
    assert re.search(r'^.*Archives.*\b1\b.*$', cap.out, re.MULTILINE)
    assert 'ERRORS for bad.zip\n\twut\n' in cap.out
    html = report.html()
    _HTMLDIR.joinpath('archives.html').write_text(html)


def test_recognition_stats(capsys):
    s1 = FileSummary(size=15, virtpath=Path('a.txt'),
                     result=CheckResult(recognizer=PlaintextChecker()))
    s2 = FileSummary(size=23, virtpath=Path('b.csv'),
                     result=CheckResult(recognizer=CSVChecker()))
    s3 = FileSummary(size=39, virtpath=Path('c.csv'),
                     result=CheckResult(recognizer=CSVChecker()))
    s4 = FileSummary(size=50, virtpath=Path('d.foo'))
    s5 = FileSummary(size=61, virtpath=Path('e.foo'))
    s6 = FileSummary(size=71, virtpath=Path('f.bar'))
    s7 = FileSummary(size=95, virtpath=Path('g'))
    report = CheckReport([s1, s2, s3, s4, s5, s6, s7])
    groups = [g for g in report.groups if 'cognized' in g.name]
    assert len(groups) == 5
    assert groups[0].name == 'Recognized by CSVChecker'
    assert groups[0].count == 2
    assert groups[0].count_pct == '29%'
    assert groups[0].size == 62
    assert groups[0].size_pct == '18%'  # 62 / 354
    assert groups[1].name == 'Recognized by PlaintextChecker'
    assert groups[1].count == 1
    assert groups[1].count_pct == '14%'
    assert groups[1].size == 15
    assert groups[1].size_pct == '4%'
    assert groups[2].name == 'Unrecognized with extension .bar'
    assert groups[2].count == 1
    assert groups[2].count_pct == '14%'
    assert groups[2].size == 71
    assert groups[2].size_pct == '20%'
    assert groups[3].name == 'Unrecognized with extension .foo'
    assert groups[3].count == 2
    assert groups[3].count_pct == '29%'
    assert groups[3].size == 111
    assert groups[3].size_pct == '31%'
    assert groups[4].name == 'Other unrecognized'
    assert groups[4].count == 1
    assert groups[4].count_pct == '14%'
    assert groups[4].size == 95
    assert groups[4].size_pct == '27%'
    report.print()
    cap = capsys.readouterr()
    assert re.search(r'^.*Recognized by CSVChecker.*\b18%.*$',
                     cap.out, re.MULTILINE)
    assert re.search(r'^.*Recognized by PlaintextChecker.*\b4%.*$',
                     cap.out, re.MULTILINE)
    assert re.search(r'^.*Unrecognized with extension \.bar.*\b20%.*$',
                     cap.out, re.MULTILINE)
    assert re.search(r'^.*Unrecognized with extension \.foo.*\b31%.*$',
                     cap.out, re.MULTILINE)
    assert re.search(r'^.*Other unrecognized.*\b27%.*$',
                     cap.out, re.MULTILINE)
    html = report.html()
    _HTMLDIR.joinpath('recognition_stats.html').write_text(html)


def test_thumbs(capsys):
    s1 = FileSummary(
        size=15, virtpath=Path('csv1.csv'),
        result=CheckResult(
            recognizer=CSVChecker(),
            thumb=Image.open(Path('tests').joinpath('csv.png'))))
    s2 = FileSummary(
        size=23, virtpath=Path('testimage.jpg'),
        result=CheckResult(
            recognizer=ImageChecker(),
            thumb=Image.open(Path('tests').joinpath('image.png'))))
    s3 = FileSummary(
        size=39, virtpath=Path('text.txt'),
        result=CheckResult(
            recognizer=PlaintextChecker(),
            thumb=Image.open(Path('tests').joinpath('plaintext.png'))))
    s4 = FileSummary(
        size=50, virtpath=Path('csv2.csv'),
        result=CheckResult(
            recognizer=QLChecker(),
            thumb=Image.open(Path('tests').joinpath('quicklook.png'))))
    s5 = FileSummary(
        size=61, virtpath=Path('other.txt'),
        result=CheckResult(recognizer=PlaintextChecker()))
    report = CheckReport([s1, s2, s3, s4, s5])
    assert report.thumb_summaries == [s1, s2, s3, s4]
    groups = [g for g in report.groups if g.name == 'Files with thumbnails']
    assert len(groups) == 1
    assert groups[0].count == 4
    assert groups[0].size == 127
    assert groups[0].count_pct == '80%'
    assert groups[0].size_pct == '68%'  # 127/188
    report.print()
    cap = capsys.readouterr()
    assert re.search(r'^.*thumbnails.*\b68%.*$', cap.out, re.MULTILINE)
    html = report.html()
    _HTMLDIR.joinpath('thumbs.html').write_text(html)
