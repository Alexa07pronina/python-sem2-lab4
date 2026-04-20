from src.source.file_source import FileSource
import pytest

def test_file_not_found():
    """тест несуществующего файла"""
    source = FileSource("aaa.txt")
    with pytest.raises(FileNotFoundError):
        list(source.get_tasks())

def test_file_source_missing_keys(tmp_path):
    """Тест неверный формат ключей"""
    filepath=tmp_path / "bad_test.txt"
    filepath.write_text('{"priority": 1}\n{"payload": {}}',encoding="utf-8")
    source = FileSource(str(filepath))
    with pytest.raises(KeyError):
        list(source.get_tasks())

def test_file_source_invalid_json(tmp_path):
    """Неверный формат json"""
    filepath = tmp_path / "bad_test.txt"
    filepath.write_text('{"priority": 1,""}',encoding="utf-8")
    source = FileSource(str(filepath))
    with pytest.raises(ValueError):
        list(source.get_tasks())

def test_file_source_empty_file(tmp_path):
    """Тест пустого файла"""
    filepath = tmp_path/"empty.txt"
    filepath.write_text("",encoding="utf-8")
    source = FileSource(str(filepath))
    assert list(source.get_tasks()) == []

def test_file_source_correct(tmp_path):
    """Корректный тест"""
    filepath = tmp_path/"test.txt"
    filepath.write_text('{"priority": 1,"payload": {"a":"b"} }\n\n{"priority": 5,"payload": {"b":"c"} }',encoding="utf-8")
    source = FileSource(str(filepath))
    tasks = source.get_tasks()
    assert hasattr(tasks, '__next__')
    first = next(tasks)
    assert first.priority == 1

    tasks_l = list(tasks)

    assert len(tasks_l) == 1 # в генерераторе осталась вторая задача
    assert len(list(tasks)) == 0 # генератор пуст
