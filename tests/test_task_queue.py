from src.models import Task, TaskStatus
from src.queue import TaskQueue
from src.source.fake_api_source import FakeApiSource
from src.source.file_source import FileSource
from src.source.generate_source import GeneratorSource


def test_task_queue_empty():
    """Пустая очередь: без источника или нулевая генерация"""
    assert len(TaskQueue(None)) == 0
    assert list(TaskQueue(None)) == []

    queue = TaskQueue(GeneratorSource(0))
    assert len(queue) == 0
    assert list(queue) == []


def test_task_queue_iterable(tmp_path):
    """TaskQueue поддерживает итерацию"""
    path = tmp_path / "tasks.txt"
    path.write_text(
        '{"payload": {"i": 0}}\n{"payload": {"i": 1}}\n{"payload": {"i": 2}}\n',
        encoding="utf-8",
    )
    queue = TaskQueue(FileSource(str(path)))

    result = [task.payload["i"] for task in queue]

    assert result == [0, 1, 2]


def test_task_queue_supports_list():
    """TaskQueue совместим с list()"""
    queue = TaskQueue(GeneratorSource(3, seed=42))
    assert len(queue)==3
    result = list(queue)
    assert len(result) == 3
    assert all(isinstance(t, Task) for t in result)


def test_task_queue_supports_sum(tmp_path):
    """Сумма приоритетов по обходу очереди"""
    path = tmp_path / "priorities.txt"
    path.write_text(
        '{"payload": {}, "priority": 1}\n'
        '{"payload": {}, "priority": 2}\n'
        '{"payload": {}, "priority": 3}\n',
        encoding="utf-8",
    )
    queue = TaskQueue(FileSource(str(path)))

    total = sum(task.priority for task in queue)

    assert total == 6


def test_task_queue_repeated_iteration():
    """Повторный обход """
    queue = TaskQueue(GeneratorSource(3, seed=0))
    assert len(list(queue)) == 3
    assert len(list(queue)) == 3
    assert len(queue) == 3


def test_task_queue_filter_by_status():
    """filter_by_status лениво отдаёт задачи с нужным статусом"""
    src = FakeApiSource("https://test.local")
    t_pending, t_done, _ = src._tasks
    t_done.start()
    t_done.complete()

    queue = TaskQueue(src)
    filtered = queue.filter_by_status(TaskStatus.PENDING)
    assert hasattr(filtered, "__next__")

    result = list(filtered)
    assert len(result) == 2
    assert all(t.status == TaskStatus.PENDING for t in result)
    assert t_pending in result


def test_task_queue_filter_by_priority(tmp_path):
    """filter_by_priority по FileSource"""
    path = tmp_path / "mix.txt"
    path.write_text(
        '{"payload": {}, "priority": 1}\n'
        '{"payload": {}, "priority": 3}\n'
        '{"payload": {}, "priority": 5}\n',
        encoding="utf-8",
    )
    queue = TaskQueue(FileSource(str(path)))

    filtered = list(queue.filter_by_priority(3))

    assert len(filtered) == 1
    assert filtered[0].priority == 3


def test_task_queue_filter_by_ready():
    """filter_by_ready: те же объекты Task в FakeApiSource сохраняют состояние"""
    src = FakeApiSource("https://test.local")
    first, *_ = src._tasks
    first.start()

    queue = TaskQueue(src)
    ready = list(queue.filter_by_ready())
    assert len(ready) == 2


def test_task_queue_iter_returns_new_iterator():
    """__iter__ возвращает новый итератор каждый раз."""
    queue = TaskQueue(GeneratorSource(3, seed=0))

    iter1 = iter(queue)
    iter2 = iter(queue)
    assert iter1 is not iter2
    assert next(iter1).payload == next(iter2).payload

    queue2=TaskQueue(GeneratorSource(3)) #без сида
    iter1=iter(queue2)
    iter2=iter(queue2)
    assert next(iter1).payload != next(iter2).payload
