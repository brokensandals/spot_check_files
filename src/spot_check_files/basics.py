from importlib import resources
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from spot_check_files import _monoid_font
from spot_check_files.checker import Checker, CheckRequest, CheckResult


_FONTS = []


def _font():
    if not _FONTS:
        with resources.path(_monoid_font, 'Monoid-Regular.ttf') as path:
            _FONTS.append(ImageFont.truetype(str(path)))
    return _FONTS[0]


def text_thumb(text: str) -> bytes:
    """Builds a PNG thumbnail for the given text."""
    img = Image.new('L', (300, 300), color=255)
    draw = ImageDraw.Draw(img)
    draw.multiline_text((0, 0), text, fill=0, font=_font())
    io = BytesIO()
    img.save(io, 'png')
    return io.getvalue()


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
