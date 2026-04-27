import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.executor import AsyncExecutor
from src.models import Task, TaskStatus
from src.special_errors import ExecutorNotStartedError, TaskProcessingError, ExecutorError
from src.handlers import HighPriorityHandler, LowPriorityHandler


@pytest.mark.asyncio
async def test_executor_basic_workflow():
    """Базовый тест: задача проходит весь цикл (PENDING → IN_PROGRESS → COMPLETED)"""
    async with AsyncExecutor(workers=1, queue_size=4) as executor:
        await executor.register_handler(HighPriorityHandler())
        await executor.register_handler(LowPriorityHandler())

        task = Task(payload={"test": True}, priority=2)
        assert task.status == TaskStatus.PENDING
        await executor.submit(task)
        await executor.wait_all()
        assert task.status == TaskStatus.COMPLETED
        assert len(executor.errors) == 0


@pytest.mark.asyncio
async def test_executor_not_started():
    """Попытка submit() без async with должна выбросить ошибку"""
    executor = AsyncExecutor()

    with pytest.raises(ExecutorNotStartedError):
        task = Task(payload={}, priority=1)
        await executor.submit(task)


@pytest.mark.asyncio
async def test_executor_error_handling():
    """Если хендлер падает — задача переходит в FAILED, ошибка сохраняется"""

    class FailingHandler:
        def can_handle(self, task: Task) -> bool:
            return True

        async def handle(self, task: Task, worker: str) -> None:
            try:
                task.start()
                raise RuntimeError("Test failure")
            except Exception as e:
                if task.status == TaskStatus.IN_PROGRESS:
                    task.fail()
                raise

    async with AsyncExecutor(workers=1) as executor:
        await executor.register_handler(FailingHandler())

        task = Task(payload={}, priority=3)
        await executor.submit(task)
        await executor.wait_all()

        assert task.status == TaskStatus.FAILED
        assert len(executor.errors) == 1
        assert isinstance(executor.errors[0], TaskProcessingError)


@pytest.mark.asyncio
async def test_executor_priority_routing():
    """Проверка: задачи с priority >= 4 идут в HighPriorityHandler """
    mock_high = MagicMock(spec=HighPriorityHandler)
    mock_high.can_handle = lambda task: task.priority >= 4
    mock_high.handle = AsyncMock()

    mock_low = MagicMock(spec=LowPriorityHandler)
    mock_low.can_handle = lambda task: task.priority < 4
    mock_low.handle = AsyncMock()

    async with AsyncExecutor(workers=1) as executor:
        await executor.register_handler(mock_high)
        await executor.register_handler(mock_low)

        task_high = Task(payload={}, priority=5)
        task_low = Task(payload={}, priority=2)

        await executor.submit(task_high)
        await executor.submit(task_low)
        await executor.wait_all()
        assert mock_high.handle.call_count == 1
        assert mock_low.handle.call_count == 1


@pytest.mark.asyncio
async def test_executor_no_handlers():
    """Проверка: ошибка если нет зарегистрированных хендлеров"""
    async with AsyncExecutor(workers=1) as executor:
        task = Task(payload={}, priority=3)
        await executor.submit(task)
        await executor.wait_all()

        assert len(executor.errors) == 1
        assert isinstance(executor.errors[0], ExecutorError)
        assert task.status == TaskStatus.PENDING

@pytest.mark.asyncio
async def test_executor_invalid_handler():
    """Проверка: нельзя зарегистрировать объект без протокола."""
    executor = AsyncExecutor()

    class BadHandler:
        pass

    with pytest.raises(TypeError, match="Хендлер не удовлетворяет протоколу"):
        await executor.register_handler(BadHandler())
