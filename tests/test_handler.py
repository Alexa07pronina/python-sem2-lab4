import pytest
from unittest.mock import AsyncMock, patch
from src.models import Task
from src.handlers import LowPriorityHandler, HighPriorityHandler

@pytest.mark.asyncio
async def test_low_priority_handler_success():
    """хендлер низкого приоритета """
    handler = LowPriorityHandler()
    task = Task(payload={"Test Low":"1"}, priority=2)
    #мокем sleep, чтобы не ждать несколько секунд
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        #мокаем логирование, чтобы изолировать тест от файловой системы
        with patch('src.handlers.log_info', new_callable=AsyncMock) as mock_log:
            await handler.handle(task,"Test Low")
            mock_sleep.assert_called_once_with(2 * 0.5)
            assert mock_log.call_count == 3


@pytest.mark.asyncio
async def test_high_priority_handler_success():
    """хендлер высокого приоритета """
    handler = HighPriorityHandler()
    task = Task(payload={"Test High":""}, priority=4)

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        with patch('src.handlers.log_info', new_callable=AsyncMock) as mock_log:
            await handler.handle(task,"Test High")
            mock_sleep.assert_called_once_with(4 * 0.1)
            assert mock_log.call_count == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("priority,expected_delay,handler_cls", [
    (1, 0.5, LowPriorityHandler),
    (3, 1.5, LowPriorityHandler),
    (4, 0.4, HighPriorityHandler),
    (5, 0.5, HighPriorityHandler),
])
async def test_handler_sleep_calculation(priority, expected_delay, handler_cls):
    """Параметризованный тест: проверяем формулу задержки для разных приоритетов."""
    handler = handler_cls()
    task = Task(payload={"Param Test":""}, priority=priority)

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        with patch('src.handlers.log_info', new_callable=AsyncMock):
            await handler.handle(task,"Test")
            mock_sleep.assert_called_once_with(expected_delay)