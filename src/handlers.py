import asyncio
from src.models import Task
from src.logging_config import log_info

class LowPriorityHandler:
    """Обработчик задач с низким приоритетом"""
    def can_handle(self, task: Task) -> bool:
        return task.priority <= 3
    async def handle(self, task: Task,worker:str) -> None:
        try:
            await log_info(f"Обрабатываем задачу {task.id[:8]} с priority={task.priority}")
            task.start()
            await log_info(f"{worker}: Задача {task.id[:8]} запущена")
            await asyncio.sleep(task.priority*0.5)
            task.complete()
            await log_info(f"{worker}: Задача {task.id[:8]} завершена")
        except Exception as e:
            if task.status == "in_progress":
                task.fail()
            await log_info(f" LowPriority ошибка: {task.id[:8]} - {e}")
            raise

class HighPriorityHandler:
    """Обработчик задач с высоким приоритетом"""

    def can_handle(self, task: Task) -> bool:
        return task.priority >= 4

    async def handle(self, task: Task, worker: str) -> None:
        try:
            await log_info(f"Обрабатываем задачу {task.id[:8]} с priority={task.priority}")
            task.start()
            await log_info(f"{worker}: Задача {task.id[:8]} запущена")
            await asyncio.sleep(task.priority * 0.1)
            task.complete()
            await log_info(f"{worker}: Задача {task.id[:8]} завершена")
        except Exception as e:
            if task.status == "in_progress":
                task.fail()
            await log_info(f" HighPriority ошибка: {task.id[:8]} - {e}")
            raise
