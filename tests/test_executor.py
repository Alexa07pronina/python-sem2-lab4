import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.executor import AsyncExecutor
from src.models import Task, TaskStatus
from src.special_errors import ExecutorNotStartedError, TaskProcessingError


@pytest.mark.asyncio
async def test_executor_basic_workflow():
    """Базовый тест: задача проходит весь цикл (PENDING → IN_PROGRESS → COMPLETED)"""
    async with AsyncExecutor(workers=1, queue_size=4) as executor:
        task = Task(payload={"test": True}, priority=2)

        assert task.status == TaskStatus.PENDING
        await executor.submit(task)
        await executor.wait_all()
        assert task.status == TaskStatus.COMPLETED
        assert len(executor.errors) == 0


@pytest.mark.asyncio
async def test_executor_not_started():
    """Попытка submit() без async with должна выбросить ошибку """
    executor = AsyncExecutor()

    with pytest.raises(ExecutorNotStartedError):
        task = Task(payload={}, priority=1)
        await executor.submit(task)


@pytest.mark.asyncio
async def test_executor_error_handling():
    """Если обработчик падает — задача переходит в FAILED, ошибка сохраняется"""
    class FailingHandler:
        async def handle(self, task):
            raise RuntimeError("Test failure")

    async with AsyncExecutor(workers=1) as executor:
        executor._handlers = {'high': FailingHandler(), 'low': FailingHandler()}

        task = Task(payload={}, priority=3)
        await executor.submit(task)
        await executor.wait_all()

        assert task.status == TaskStatus.FAILED
        assert len(executor.errors) == 1
        assert isinstance(executor.errors[0], TaskProcessingError)


@pytest.mark.asyncio
async def test_executor_priority_routing():
    """Проверка, что задачи с priority >= 4 идут в HighPriorityHandler"""
    with patch('src.executor.HighPriorityHandler') as MockHigh, patch('src.executor.LowPriorityHandler') as MockLow:
        mock_high = MockHigh.return_value
        mock_low = MockLow.return_value
        mock_high.handle = AsyncMock()
        mock_low.handle = AsyncMock()

        async with AsyncExecutor(workers=1) as executor:
            task_high = Task(payload={}, priority=5)
            task_low = Task(payload={}, priority=2)

            await executor.submit(task_high)
            await executor.submit(task_low)
            await executor.wait_all()
            mock_high.handle.assert_called_once_with(task_high)
            mock_low.handle.assert_called_once_with(task_low)

