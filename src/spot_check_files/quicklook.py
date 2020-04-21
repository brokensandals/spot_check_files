from pathlib import Path
import shutil
import subprocess
import tempfile
from spot_check_files.checker import Checker, CheckResult, CheckRequest


class QLChecker(Checker):
    def __str__(self):
        return 'QLChecker'

    """Checks files using QuickLook (MacOS only).

    This invokes the qlmanage command-line app and is fairly slow, but
    QuickLook can recognize a wide variety of file types and generates nice
    thumbnails.

    A file is assumed to be "valid" if QuickLook generates a thumbnail for it.
    If it doesn't, the checker will not mark the result as recognized.
    """
    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()

        outdir = tempfile.mkdtemp(dir=req.tmpdir)
        subprocess.check_output(
            ['qlmanage', '-t', '-s', '300',
             str(req.realpath), '-o', outdir])

        paths = list(Path(outdir).glob('*.png'))
        if paths:
            result.recognizer = self
            if req.png:
                result.png = paths[0].read_bytes()
        else:
            result.errors.append('no png produced by qlmanage')

        shutil.rmtree(outdir)

        return result
