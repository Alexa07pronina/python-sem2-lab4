"""Тесты для модуля неблокирующего логирования."""

import logging
import pytest

from src.logging_config import setup_logging,log_debug, log_info, log_warning


@pytest.fixture(autouse=True)
def reset_lab4_logger():
    """Автоматически очищает логгер 'lab4' перед и после каждого теста"""
    logger = logging.getLogger("lab4")
    logger.handlers.clear()
    yield
    logger.handlers.clear()
    logging.shutdown()


@pytest.mark.asyncio
async def test_setup_logging_adds_handlers(tmp_path):
    """Проверка: при вызове setup_logging добавляются FileHandler и StreamHandler"""
    log_file = tmp_path / "test_setup.log"
    logger, _ = setup_logging(log_file=str(log_file), mode="w")

    handlers = {type(h).__name__: h for h in logger.handlers}
    assert "FileHandler" in handlers
    assert "StreamHandler" in handlers

    assert handlers["FileHandler"].level == logging.INFO
    assert handlers["StreamHandler"].level == logging.ERROR


@pytest.mark.asyncio
async def test_file_handler_writes_info_and_above(tmp_path):
    """Проверка: в файл пишутся только сообщения >= INFO"""
    log_file = tmp_path / "test_file.log"
    setup_logging(log_file=str(log_file), mode="w")

    await log_debug("Debug msg")
    await log_info("Info msg")
    await log_warning("Warn msg")

    content = log_file.read_text(encoding="utf-8")
    assert "Debug msg" not in content
    assert "Info msg" in content
    assert "Warn msg" in content

@pytest.mark.asyncio
async def test_formatter_applies_correct_format(tmp_path):
    """Проверка: форматтер записывает время, имя и уровень"""
    log_file = tmp_path / "test_format.log"
    setup_logging(log_file=str(log_file), mode="w")

    await log_info("Format check")
    content = log_file.read_text(encoding="utf-8")
    assert "lab4" in content
    assert "INFO" in content
    assert "Format check" in content
    assert ":" in content.split("|")[0].strip()