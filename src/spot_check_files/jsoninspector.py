import json
from spot_check_files.base import\
    BodyCallback, ChildCallback, FileInfo, Inspector


def _discard(_):
    return None


class JSONInspector(Inspector):
    def name(self):
        return 'json'

    def inspect(self, info: FileInfo, get_data: BodyCallback, *,
                on_child: ChildCallback = None,
                thumbnail: bool = False) -> None:
        with get_data() as data:
            try:
                json.load(data, object_hook=_discard)
                info.recognized = True
            except json.JSONDecodeError:
                info.problems.append('invalid json')

            # TODO: thumbnail
