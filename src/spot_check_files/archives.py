from pathlib import Path
import tarfile
import tempfile
import zipfile
from zipfile import ZipFile
from spot_check_files.checker import Checker, CheckResult, CheckRequest


class ZipChecker(Checker):
    """Extracts zip files."""
    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()

        try:
            if not zipfile.is_zipfile(req.path):
                result.errors.append('not a zipfile')
                return result

            result.recognizer = self

            with ZipFile(req.path, 'r') as zf:
                result.extracted = Path(tempfile.mkdtemp(dir=req.tmpdir))
                zf.extractall(result.extracted)
        except Exception as e:
            result.errors.append(e)

        return result


class TarChecker(Checker):
    """Extracts tar files.

    Tars may be compressed with any formats the python tarfile lib supports,
    including gz, bz2, and xz.
    """
    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()

        try:
            if not tarfile.is_tarfile(req.path):
                result.errors.append('not a tarfile')
                return result

            result.recognizer = self

            with tarfile.open(req.path, 'r') as tf:
                result.extracted = Path(tempfile.mkdtemp(dir=req.tmpdir))
                tf.extractall(result.extracted)
        except Exception as e:
            result.errors.append(e)

        return result
