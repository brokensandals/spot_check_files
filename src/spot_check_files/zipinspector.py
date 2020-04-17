from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile
from spot_check_files.base import\
    ChildCallback, FileAccessor, FileInfo, FSFileAccessor, Inspector,\
    IOFileAccessor


class ZipInspector(Inspector):
    def _inspect_zipfile(self, info: FileInfo, zf: zipfile.ZipFile,
                         on_child: ChildCallback):
        raise NotImplementedError()

    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False):
        with accessor.agnostic() as file:
            if not zipfile.is_zipfile(file):
                info.problems.append('not a zipfile')
                return

            info.mere_container = True
            info.recognized = True

            with zipfile.ZipFile(file, 'r') as zf:
                self._inspect_zipfile(info, zf, on_child)


class StreamingZipInspector(ZipInspector):
    def _inspect_zipfile(self, info, zf, on_child):
        if zf.testzip():
            info.problems.append('zip contains at least one invalid entry')
        for zi in zf.infolist():
            fi = FileInfo(
                pathseq=info.pathseq + (zi.filename,),
                size=zi.file_size)

            child_acc = IOFileAccessor(
                fi.pathseq, lambda: zf.open(zi, 'r'))

            try:
                if on_child:
                    on_child(fi, child_acc)
            except zipfile.BadZipFile:
                fi.problems.append('corrupt in zip')


class ExtractingZipInspector(ZipInspector):
    def _inspect_zipfile(self, info, zf, on_child):
        try:
            with TemporaryDirectory() as tmpdir:
                zf.extractall(tmpdir)
                for path in Path(tmpdir).glob('**/*'):
                    if not path.is_file():
                        continue

                    rel_path = path.relative_to(tmpdir)
                    fi = FileInfo(
                        pathseq=info.pathseq + (str(rel_path),),
                        size=path.stat().st_size)

                    child_acc = FSFileAccessor(path)

                    if on_child:
                        on_child(fi, child_acc)
        except zipfile.BadZipFile:
            info.problems.append('zip contains at least one invalid entry')
