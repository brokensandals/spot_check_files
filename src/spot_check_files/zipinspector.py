from contextlib import contextmanager
import zipfile


class ZipInspector:
    def __init__(self, file, vpath=None):
        if zipfile.is_zipfile(file):
            self.zip = zipfile.ZipFile(file, 'r')
        else:
            self.zip = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        if self.zip:
            self.zip.close()

    def filenames(self):
        if not self.zip:
            return []
        return [i.filename for i in self.zip.infolist() if not i.is_dir()]

    def problems(self):
        if not self.zip:
            return ['not a zipfile']
        failed = self.zip.testzip()
        if failed:
            return [f'zip contains at least one invalid entry: {failed}']
        return []

    @contextmanager
    def extract(self, filename):
        if not self.zip:
            raise KeyError(f'cannot extract {filename} from non-zipfile')
        with self.zip.open(filename, 'r') as file:
            yield file
