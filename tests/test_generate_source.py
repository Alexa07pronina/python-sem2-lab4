from src.source.generate_source import GeneratorSource


def test_generate_source():
    """ тест генеративного источника"""
    source = GeneratorSource(5)
    tasks = source.get_tasks()
    tasks_l = list(tasks)
    assert hasattr(tasks, '__iter__')
    assert hasattr(tasks, '__next__')

    assert len(tasks_l)==5
    assert 1<=tasks_l[0].priority<=5
