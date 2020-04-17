from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from spot_check_files.base import ChildCallback, FileAccessor, FileInfo,\
    FSFileAccessor, Inspector, IOFileAccessor


class TarInspector(Inspector):
    def _inspect_tarfile(self, info: FileInfo, accessor: FileAccessor,
                         on_child: ChildCallback):
        raise NotImplementedError()

    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        try:
            self._inspect_tarfile(info, accessor, on_child)
        except:
            info.problems.append('error while inspecting')


class StreamingTarInspector(TarInspector):
    def _inspect_tarfile(self, info: FileInfo, accessor: FileAccessor,
                         on_child: ChildCallback):
        with accessor.io() as data:
            with tarfile.open(mode='r', fileobj=data) as tf:
                info.mere_container = True
                info.recognized = True

                for ti in tf:
                    if not ti.isreg():
                        continue

                    fi = FileInfo(
                        pathseq=info.pathseq + (ti.name,),
                        size=ti.size)

                    child_acc = IOFileAccessor(
                        fi.pathseq, lambda: tf.extractfile(ti))

                    try:
                        if on_child:
                            on_child(fi, child_acc)
                    except tarfile.TarError:
                        fi.problems.append('unable to extract from tar')


class ExtractingTarInspector(TarInspector):
    def _inspect_tarfile(self, info: FileInfo, accessor: FileAccessor,
                         on_child: ChildCallback):
        with accessor.path() as path:
            if not tarfile.is_tarfile(path):
                info.problems.append('not a tarfile')
                return

            info.mere_container = True
            info.recognized = True

            with tarfile.open(path, 'r') as tf:
                with TemporaryDirectory() as tmpdir:
                    tf.extractall(tmpdir)
                    for childpath in Path(tmpdir).glob('**/*'):
                        if not childpath.is_file():
                            continue

                        relpath = childpath.relative_to(tmpdir)
                        fi = FileInfo(
                            pathseq=info.pathseq + (str(relpath),),
                            size=childpath.stat().st_size)

                        child_acc = FSFileAccessor(childpath)

                        if on_child:
                            on_child(fi, child_acc)
