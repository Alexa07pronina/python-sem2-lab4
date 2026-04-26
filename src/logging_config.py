import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

# Глобальный логгер
_logger: Optional[logging.Logger] = None


def setup_logging(
        level: str = "INFO",
        log_file: str = "lab4.log",
        mode: str = "w"
) -> Tuple[logging.Logger, None]:
    """Настройка логирования """
    global _logger

    _logger = logging.getLogger("lab4")
    _logger.setLevel(logging.DEBUG)
    _logger.handlers.clear()
    _logger.propagate = False

    file_path = Path(log_file).resolve()
    file_handler = logging.FileHandler(
        file_path,
        mode=mode,
        encoding="utf-8",
        delay=True
    )
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    ))

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)-8s | %(message)s"
    ))

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)
    _logger.info("Логирование запущено (файл: %s, консоль: только ошибки)", log_file)
    return _logger, None

async def log(msg: str, level: int = logging.INFO) -> None:
    """Неблокирующая запись лога через asyncio.to_thread """
    if _logger is not None:
        await asyncio.to_thread(_logger.log, level, msg)

async def log_debug(msg: str) -> None:
    await log(msg, logging.DEBUG)
async def log_info(msg: str) -> None:
    await log(msg, logging.INFO)
async def log_warning(msg: str) -> None:
    await log(msg, logging.WARNING)
async def log_error(msg: str) -> None:
    await log(msg, logging.ERROR)


def shutdown_logging(handlers: Optional[Tuple]) -> None:
    """Остановить логирование """
    if _logger:
        for handler in _logger.handlers:
            handler.flush()
            handler.close()
    logging.shutdown()