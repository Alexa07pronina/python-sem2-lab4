from src.loader import fetch_tasks
from src.models import Task
from src.protocols import TaskSource
import pytest


class TestSource:
    def get_tasks(self):
        yield Task(payload={})
        yield Task(payload={"status": "ok"})


class FakeSource:
    pass


def test_fetch_tasks():
    """Проверка источника: возвращается TaskSource, get_tasks() можно вызывать повторно."""
    source_true = TestSource()
    source_fake = FakeSource()
    validated = fetch_tasks(source_true)
    assert isinstance(validated, TaskSource)
    assert len(list(validated.get_tasks())) == 2
    assert len(list(validated.get_tasks())) == 2
    with pytest.raises(TypeError):
        fetch_tasks(source_fake)
