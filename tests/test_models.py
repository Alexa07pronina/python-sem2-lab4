from src.models import Task
from src.task_errors import InvalidStatusError,InvalidPriorityError
import pytest

def test_task_model():
    """ Тест модели"""
    task = Task(payload={"key1":"value1","key2":"value2","key3":"value3"})
    assert task.payload == {"key1":"value1","key2":"value2","key3":"value3"}
    assert task.priority == 3
    assert isinstance(task, Task)
    assert isinstance(task.id,str)
    assert isinstance(task.payload,dict)
    assert task.is_ready

    with pytest.raises(AttributeError):
        task.id = "12345"
    with pytest.raises(InvalidPriorityError):
        task.priority=10
    with pytest.raises(TypeError):
        task.priority="1"
    with pytest.raises(InvalidStatusError):
        task.status="something"
    with pytest.raises(TypeError):
        task.status=100

    task.start()
    assert task.status == "in_progress"
    task.fail()
    assert task.status == "failed"
    task.retry()
    assert task.status == "pending"
    task.start()
    task.complete()
    assert task.status == "completed"
