import logging
from typing import Any, Iterator, Optional

from src.models import Task
from src.protocols import TaskSource

logger = logging.getLogger(__name__)


class TaskQueue:
    """Очередь задач"""
    __slots__ = ("_source",)

    def __init__(self, source: Optional[TaskSource] = None) -> None:
        self._source = source

    def _iter_tasks(self) -> Iterator[Task]:
        """Внутренний генератор: один проход по потоку задач из текущего источника"""
        if self._source is not None:
            yield from self._source.get_tasks()

    def __len__(self) -> int:
        """Количество задач в очереди"""
        return sum(1 for _ in self._iter_tasks())

    def __iter__(self) -> Iterator[Task]:
        """Реализует протокол итерируемого объекта: возвращает новый итератор по задачам очереди для использования в for, list() и т.п"""
        return self._iter_tasks()

    def filter(self, *, field: str, value: Any) -> Iterator[Task]:
        """Фильтрация задач по публичному полю/свойству Task и ожидаемому значению.
        """
        it = iter(self._iter_tasks())
        first = next(it,None)
        if first is None:
            return
        try:
            getattr(first, field)
        except AttributeError as e:
            raise ValueError(f"неизвестное поле: {field!r}") from None

        if getattr(first, field) == value:
            yield first
        for task in it:
            if getattr(task, field) == value:
                yield task
