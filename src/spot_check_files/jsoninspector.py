import json
from spot_check_files.base import\
    ChildCallback, FileAccessor, FileInfo, Inspector


def _discard(_):
    return None


class JSONInspector(Inspector):
    def name(self):
        return 'json'

    def inspect(self, info: FileInfo, accessor: FileAccessor, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        with accessor.io() as data:
            try:
                json.load(data, object_hook=_discard)
                info.recognized = True
            except json.JSONDecodeError:
                info.problems.append('invalid json')

            # TODO: thumbnail
