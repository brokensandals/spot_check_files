import zipfile
from spot_check_files.base import\
    ChildCallback, FileAccessor, FileInfo, Inspector, IOFileAccessor


class ZipInspector(Inspector):
    def name(self):
        return 'zip'

    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False):
        with accessor.io() as data:
            if not zipfile.is_zipfile(data):
                info.problems.append('not a zipfile')
                return

            info.mere_container = True
            info.recognized = True

            with zipfile.ZipFile(data, 'r') as zf:
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
