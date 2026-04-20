from src.protocols import TaskSource


def fetch_tasks(source: TaskSource) -> TaskSource:
    """Проверяет контракт и возвращает источник для повторных вызовов get_tasks()"""
    if not isinstance(source, TaskSource):
        raise TypeError(f"{source} не соответствует контракту TaskSource")
    return source
