import logging
import asyncio
import random
from src.models import Task
from src.special_errors import ExecutorNotStartedError, TaskProcessingError
from src.handlers import HighPriorityHandler, LowPriorityHandler
from src.protocols import TaskHandler
from typing import Optional
from src.logging_config import (log_info, log_warning, log_error)

class AsyncExecutor:
    """Асинхронный исполнитель задач"""
    def __init__(self, workers:int = 2, queue_size:int = 5)-> None:
        self._workers = workers
        self._queue:Optional[asyncio.Queue]=None
        self._queue_size = queue_size
        self._handlers:dict = {'high': HighPriorityHandler(), 'low': LowPriorityHandler()}
        self._worker_tasks:list[asyncio.Task] = list()
        self._running:bool = False
        self._errors:list[TaskProcessingError] = list()
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
    def _select_handler(self, task:Task) -> TaskHandler:
        """Выбор обработчика в зависимости от приоритета задачи"""
        if task.priority>3: return self._handlers['high']
        return self._handlers['low']

    async def wait_all(self)->None:
        """Ожидание завершения всех задач"""
        if self._queue:
            await self._queue.join()
    async def submit(self, task:Task) -> None:
        """Отправка задачи на выполнение"""
        if self._queue is None or not self._running:
            raise ExecutorNotStartedError()
        await self._queue.put(task)

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
                task.start()
                await log_info(f"{name}: Задача {task.id[:8]} запущена")
                handler = self._select_handler(task)
                await handler.handle(task)
                random.seed(67)
                rand_num=random.randint(1,100)
                if '6' in str(rand_num) or '7' in str(rand_num):
                    task.fail()
                else:
                    task.complete()
                await log_info(f"{name}: Задача {task.id[:8]} завершена")
            except Exception as e:
                await log_error(f"{name}: ошибка {task.id[:8]}: {e}")
                error = TaskProcessingError(f"{task.id[:8]}: {e}")
                self._errors.append(error)
                if task.status == 'in_progress':
                    task.fail()
                    await log_warning(f"{name}: задача {task.id[:8]} помечена как failed")
            finally:
                self._queue.task_done()
