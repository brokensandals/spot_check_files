import csv
from importlib import resources
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import List
from spot_check_files import _monoid_font
from spot_check_files.checker import Checker, CheckRequest, CheckResult


_FONTS = []


def _font():
    if not _FONTS:
        with resources.path(_monoid_font, 'Monoid-Regular.ttf') as path:
            _FONTS.append(ImageFont.truetype(str(path), 8))
    return _FONTS[0]


def table_thumb(rows: List[List[str]]) -> bytes:
    """Builds a PNG thumbnail for a table."""
    img = Image.new('L', (300, 300), color=255)
    draw = ImageDraw.Draw(img)
    font = _font()
    height = draw.textsize(' ')[1] + 5
    x = 0

    def rowcol(r, c):
        if c < len(r):
            return r[c]
        else:
            return ''

    for col in range(len(rows[0])):
        maxlen = min(max(len(rowcol(r, col)) for r in rows), 30)
        y = 0
        for row in rows:
            text = rowcol(row, col).replace('\n', '\\n')[0:maxlen]
            draw.text((x, y), text, fill=0, font=font)
            y += height
        x += draw.textsize(' ' * maxlen, font=font)[0] + 5
        draw.line([(x, 2), (x, y - 2)], fill=128)
        x += 5
    io = BytesIO()
    img.save(io, 'png')
    return io.getvalue()


def text_thumb(text: str) -> bytes:
    """Builds a PNG thumbnail for the given text."""
    img = Image.new('L', (300, 300), color=255)
    draw = ImageDraw.Draw(img)
    draw.multiline_text((0, 0), text, fill=0, font=_font())
    io = BytesIO()
    img.save(io, 'png')
    return io.getvalue()


class CSVChecker(Checker):
    def __str__(self):
        return 'CSVChecker'

    """Checks a CSV or TSV file for problems.

    Python's csv.Sniffer is used to try to determine the column delimiter;
    if it can't figure it out, this checker will not mark the file as
    recognized.
    """
    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        try:
            rows = []
            with open(req.realpath, 'r', newline='') as file:
                dialect = csv.Sniffer().sniff(file.read(1024))
                result.recognizer = self
                file.seek(0)
                for row in csv.reader(file, dialect):
                    if req.png and len(rows) < 30:
                        rows.append(row[0:7])
                if req.png:
                    result.png = table_thumb(rows)
        except csv.Error as e:
            result.errors.append(e)
        return result


class PlaintextChecker(Checker):
    """Checks a plaintext file for encoding problems.

    This will read the input as a text file, relying on Python's default
    behavior to select the encoding. The checker will mark the file as
    recognized as long as it is able to open it. It will attempt to read
    the entire file and add an error if it cannot decode it.
    """
    def __str__(self):
        return 'PlaintextChecker'

    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        try:
            lines = []
            with open(req.realpath, 'r') as file:
                result.recognizer = self
                for line in file:
                    if req.png and len(lines) < 500:
                        lines.append(line[0:500])
                    pass
            if req.png:
                result.png = text_thumb(''.join(lines))
        except ValueError as e:
            result.errors.append(e)
        return result
