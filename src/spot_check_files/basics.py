"""Implementations of Checker for various basic file types."""
import csv
from importlib import resources
import json
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from typing import List
from xml.dom import minidom
from spot_check_files import _monoid_font
from spot_check_files.checker import Checker, CheckRequest, CheckResult


_FONTS = []


def _font():
    if not _FONTS:
        with resources.path(_monoid_font, 'Monoid-Regular.ttf') as path:
            _FONTS.append(ImageFont.truetype(str(path), 8))
    return _FONTS[0]


def table_thumb(rows: List[List[str]]) -> bytes:
    """Builds a thumbnail for a table."""
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
    return img


def text_thumb(text: str) -> bytes:
    """Builds a thumbnail for the given text."""
    img = Image.new('L', (300, 300), color=255)
    draw = ImageDraw.Draw(img)
    draw.multiline_text((0, 0), text, fill=0, font=_font())
    return img


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
                    if req.thumb and len(rows) < 30:
                        rows.append(row[0:7])
                if req.thumb:
                    result.thumb = table_thumb(rows)
        except csv.Error as e:
            result.errors.append(e)
        return result


class ImageChecker(Checker):
    """Checks an image by loading it with PIL.
    """
    def __str__(self):
        return 'ImageChecker'

    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        try:
            with Image.open(req.realpath, 'r') as img:
                img.load()
                result.recognizer = self
                if req.thumb:
                    img.thumbnail((300, 300))
                    result.thumb = img
        except OSError as e:
            # An issue I've encountered but haven't dug into yet.
            result.errors.append(e)
        except UnidentifiedImageError as e:
            result.errors.append(e)
        except ZeroDivisionError as e:
            # An issue I've encountered but haven't dug into yet.
            result.errors.append(e)
        return result


class JSONChecker(Checker):
    """Checks that a file is valid JSON.

    If the file cannot be parsed, it will not be marked as recognized.
    """
    def __str__(self):
        return 'JSONChecker'

    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        parsed = None
        with req.realpath.open('r') as file:
            try:
                parsed = json.load(file)
                result.recognizer = self
            except json.JSONDecodeError as e:
                result.errors.append(e)
        if req.thumb and parsed is not None:
            pretty = json.dumps(parsed, indent=2)
            # Don't send an excessive amount of text to Pillow
            lines = [s[0:100] for s in pretty.splitlines()[0:100]]
            result.thumb = text_thumb('\n'.join(lines))
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
                    if req.thumb and len(lines) < 100:
                        lines.append(line[0:100])
                    pass
            if req.thumb:
                result.thumb = text_thumb(''.join(lines))
        except ValueError as e:
            result.errors.append(e)
        return result


class XMLChecker(Checker):
    """Checks that a file is valid XML.

    If the file cannot be parsed, it will not be marked as recognized.
    """
    def __str__(self):
        return 'XMLChecker'

    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        parsed = None
        try:
            parsed = minidom.parse(str(req.realpath))
            result.recognizer = self
        except Exception as e:
            result.errors.append(e)
        if req.thumb and parsed is not None:
            pretty = parsed.toprettyxml(indent='  ')
            # Don't send an excessive amount of text to Pillow
            lines = [s[0:100] for s in pretty.splitlines()[0:100]]
            result.thumb = text_thumb('\n'.join(lines))
        return result
