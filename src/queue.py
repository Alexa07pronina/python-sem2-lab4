from typing import Iterator, Optional

from src.protocols import TaskSource


class TaskQueue:
    """Очередь задач"""
    __slots__ = ("_source",)

    def __init__(self, source: Optional[TaskSource] = None) -> None:
        self._source = source

    def _iter_tasks(self) -> Iterator:
        """Внутренний генератор: один проход по потоку задач из текущего источника"""
        if self._source is not None:
            yield from self._source.get_tasks()

    def __len__(self) -> int:
        """Количество задач в очереди"""
        return sum(1 for _ in self._iter_tasks())

    def __iter__(self) -> Iterator:
        """Реализует протокол итерируемого объекта: возвращает новый итератор по задачам очереди для использования в for, list() и т.п"""
        return self._iter_tasks()

    def filter_by_status(self, status: str) -> Iterator:
        """Фильтрация задач по статусу"""
        return (t for t in self._iter_tasks() if t.status == status)

    def filter_by_priority(self, priority: int) -> Iterator:
        """Фильтрация задач по приоритету"""
        return (t for t in self._iter_tasks() if t.priority == priority)

    def filter_by_ready(self) -> Iterator:
        """Фильтрация задач по готовности"""
        for task in self._iter_tasks():
            if task.is_ready:
                yield task
