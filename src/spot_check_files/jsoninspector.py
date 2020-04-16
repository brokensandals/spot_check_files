import json


class JSONInspector:
    def __init__(self, file, vpath=None):
        self.file = file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def filenames(self):
        return []

    def problems(self):
        def discard(dct):
            return None

        try:
            json.load(self.file, object_hook=discard)
        except json.JSONDecodeError:
            return ['invalid json']

        return []
