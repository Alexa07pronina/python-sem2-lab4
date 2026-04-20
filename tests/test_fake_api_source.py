from src.source.fake_api_source import FakeApiSource

def test_fake_api_source_returns_iterator():
    """Проверка, что возвращается итератор"""
    source = FakeApiSource("http://example.com")
    tasks = source.get_tasks()

    assert hasattr(tasks, '__iter__')
    assert hasattr(tasks, '__next__')
    tasks_l = list(tasks)
    assert len(tasks_l) == 3
