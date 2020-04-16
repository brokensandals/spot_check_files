from io import BytesIO
from spot_check_files.jsoninspector import JSONInspector


def test_problems_invalid():
    data = BytesIO(bytes('garbage', 'utf-8'))
    with JSONInspector(data) as inspector:
        problems = inspector.problems()
        assert inspector.problems() == ['invalid json']


def test_problems_valid():
    data = BytesIO(bytes('{"garbage": false}', 'utf-8'))
    with JSONInspector(data) as inspector:
        assert inspector.problems() == []
