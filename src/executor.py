import asyncio
import random
from src.models import Task
from src.special_errors import ExecutorNotStartedError, TaskProcessingError, ExecutorError
from src.protocols import TaskHandler
from typing import Optional,List
from src.logging_config import (log_info, log_warning, log_error)

class AsyncExecutor:
    """Асинхронный исполнитель задач"""
    def __init__(self, workers:int = 2, queue_size:int = 5)-> None:
        self._workers = workers
        self._queue:Optional[asyncio.Queue]=None
        self._queue_size = queue_size
        self._handlers: List[TaskHandler] = []
        self._worker_tasks:list[asyncio.Task] = list()
        self._running:bool = False
        self._errors:list[TaskProcessingError] = list()

    async def register_handler(self, handler: TaskHandler) -> None:
        """ Регистрация хендлеров в определенном порядке """
        if not isinstance(handler, TaskHandler):
            raise TypeError(f"Хендлер не удовлетворяет протоколу TaskHandler")
        self._handlers.append(handler)
        await log_info(f"Зарегистрирован хендлер: {handler.__class__.__name__}")

    @property
    def errors(self)->list[TaskProcessingError]:
        """ Список ошибок"""
        return list(self._errors) #вернем копию для безопасности

    async def __aenter__(self) -> 'AsyncExecutor':
        """Запуск исполнителя"""
        await log_info(f"Исполнитель запущен с workers={self._workers} и размером {self._queue_size}")
        self._running = True
        self._queue = asyncio.Queue(maxsize=self._queue_size)
        self._worker_tasks = [
            asyncio.create_task(self._worker_loop(f"worker-{i}"))
            for i in range(self._workers)
        ]
        return self

    def _select_handler(self, task: Task) -> TaskHandler:
        """ Выбор хендлера для задачи """
        if not self._handlers:
            raise ExecutorError("Нет зарегестрированных хендлеров")

        for handler in self._handlers:
            if handler.can_handle(task):
                return handler
        raise ExecutorError(f"Нет подходящих обработчиков для задачи {task.id[:8]}")

    async def wait_all(self)->None:
        """Ожидание завершения всех задач"""
        if self._queue:
            await self._queue.join()
    async def submit(self, task:Task) -> None:
        """Отправка задачи на выполнение"""
        if self._queue is None or not self._running:
            raise ExecutorNotStartedError()
        await self._queue.put(task)
        await log_info(f"Задача {task.id[:8]} отправлена в очередь")

    async def __aexit__(self, exc_type, exc_val, exc_tb)->bool:
        """Завершение исполнителя"""
        for _ in range(self._workers):
            await self._queue.put(None)
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._running = False
        await log_info("Исполнитель остановлен")
        if self._errors:
            await log_warning(f"Всего ошибок:{len(self._errors)}")
        return False

    async def _worker_loop(self, name:str)->None:
        """Цикл обработки задач"""
        await log_info(f"{name} запущен")
        while True:
            task = await self._queue.get()
            if task is None:
                self._queue.task_done()
                await log_info(f"{name} завершил работу")
                break
            try:
                await log_info(f"{name}: задача {task.id[:8]} передана хендлеру")
                handler = self._select_handler(task)
                await handler.handle(task,name)
                await log_info(f"{name}: задача {task.id[:8]} обработана хендлером")

            except Exception as e:
                await log_error(f"{name}: ошибка {task.id[:8]}: {e}")
                error = TaskProcessingError(f"[{task.id[:8]}] {e}")
                self._errors.append(error)

            finally:
                self._queue.task_done()