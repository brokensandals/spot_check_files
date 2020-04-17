from pathlib import Path
from xml import sax
from spot_check_files.base import\
    ChildCallback, FileAccessor, FileInfo, Inspector


class XMLInspector(Inspector):
    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        with accessor.agnostic() as file:
            if isinstance(file, Path):
                file = str(file)
            try:
                sax.parse(file, sax.handler.ContentHandler())
                info.recognized = True
            except sax.SAXParseException:
                info.problems.append('invalid xml')

            # TODO: thumbnail
