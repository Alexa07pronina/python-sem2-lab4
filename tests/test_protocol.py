from src.protocols import TaskSource
from src.source.fake_api_source import FakeApiSource
from src.source.file_source import FileSource
from src.source.generate_source import GeneratorSource


class FakeSource:
    pass

def test_task_protocol():
    assert isinstance(FakeApiSource("http://python-test.com"),TaskSource)
    assert isinstance(GeneratorSource(2),TaskSource)
    assert isinstance(FileSource("test.txt"),TaskSource)
    assert not isinstance(FakeSource(),TaskSource)
