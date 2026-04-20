class TaskValidationError(Exception):
    """Базовое исключение для задач """

    def __init__(self, task_id: str = None, message: str = "", extra: str = ""):
        """
        Args:
            task_id: ID задачи
            message: Базовое описание ошибки
            extra: Дополнительный текст
        """
        parts = []
        if task_id:
            parts.append(f"Задача [{task_id[:8]}...]")
        if message:
            parts.append(message)
        if extra:
            parts.append(extra)

        super().__init__(",".join(parts))


class InvalidPriorityError(TaskValidationError):
    """Приоритет вне диапазона 1-5."""

    def __init__(self, task_id: str = None, extra: str = ""):
        super().__init__(
            task_id=task_id,
            message="Некорректный приоритет",
            extra=extra
        )


class InvalidStatusError(TaskValidationError):
    """Недопустимый статус задачи."""

    def __init__(self, task_id: str = None, extra: str = ""):
        super().__init__(
            task_id=task_id,
            message="Недопустимый статус задачи",
            extra=extra
        )
