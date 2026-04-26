import asyncio
from src.models import Task
from src.logging_config import log_info

class LowPriorityHandler:
    """Обработчик задач с низким приоритетом"""
    async def handle(self, task: Task) -> None:
        await log_info(f"Обрабатываем задачу {task.id[:8]} с priority={task.priority}")
        await asyncio.sleep(task.priority*0.5)
        await log_info("Обработка завершена")

class HighPriorityHandler:
    """Обработчик задач с высоким приоритетом"""
    async def handle(self, task: Task) -> None:
        await log_info(f"Обрабатываем задачу {task.id[:8]} с priority={task.priority}")
        await asyncio.sleep(task.priority * 0.1)
        await log_info("Обработка завершена")
