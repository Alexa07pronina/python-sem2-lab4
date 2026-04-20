from typing import Protocol,runtime_checkable
from src.models import Task
from typing import Iterator

@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterator[Task]:
        """Итератор задач"""
        ...
