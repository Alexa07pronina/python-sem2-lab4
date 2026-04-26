import asyncio
from src.logging_config import setup_logging, log_info, log_warning, shutdown_logging
from src.executor import AsyncExecutor
from src.source.generate_source import GeneratorSource


async def main():
    """Точка входа для Lab 4 """
    logger, _ = setup_logging(log_file="lab4.log", mode="w")

    try:
        await log_info("Запуск исполнителя")
        source = GeneratorSource(count_task=7, seed=42)
        tasks = source.get_tasks()
        async with AsyncExecutor(workers=2, queue_size=4) as executor:
            async def producer():
                for task in tasks:
                    await executor.submit(task)
                    await log_info(f"Отправлена задача {task.id[:8]}")
            await asyncio.gather(producer(), executor.wait_all())

        if executor.errors:
            await log_warning(f"Ошибки {len(executor.errors)}:" )
            for err in executor.errors:
                await log_warning(f" {err}")
        else:
            await log_info("Все задачи обработаны успешно")
            print("Все задачи обработаны успешно")

        await log_info("Завершение")

    finally:
        shutdown_logging(None)
        print("Программа завершилась. Для подробностей смотри логи в lab4.log")


if __name__ == "__main__":
    asyncio.run(main())