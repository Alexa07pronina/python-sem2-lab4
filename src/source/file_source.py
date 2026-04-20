from src.models import Task
from typing import Iterator
import json

class FileSource:
    """Задачи из файла"""
    def __init__(self,filename:str):
        self.filename = filename

    def get_tasks(self) -> Iterator[Task]:
        try:
            with open(self.filename,'r',encoding='utf-8') as f:
                line_num=1
                for line in f:
                    line=line.rstrip()
                    if not line:
                        line_num+=1
                        continue
                    try:
                        task=json.loads(line)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Неверный JSON на строке {line_num}: {e}")

                    if not isinstance(task,dict) or 'payload' not in task:
                        raise KeyError(f"'payload' отсутсвует в строке {line_num}")
                    line_num += 1
                    yield Task(payload=task['payload'],priority=task.get('priority', 3))
        except FileNotFoundError:
            raise FileNotFoundError(f"файл {self.filename} не найден")
