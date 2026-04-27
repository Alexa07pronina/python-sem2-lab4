from typing import Protocol,runtime_checkable
from src.models import Task
from typing import Iterator

@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterator[Task]:
        """Итератор задач"""
        ...

@runtime_checkable
class TaskHandler(Protocol):

    def can_handle(self, task: Task) -> bool:
        """ Проверка возможности выполнения"""
        ...
    async def handle(self, task: Task, worker: str) -> None:
        """Обработка задачи"""
        ...
