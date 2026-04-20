from src.loader import fetch_tasks
from src.source.file_source import FileSource
from src.source.generate_source import GeneratorSource
from src.source.fake_api_source import FakeApiSource
from src.queue import TaskQueue
from pathlib import Path

def main() -> None:
    """Точка входа"""
    project_root = Path(__file__).parent.parent
    file_path = project_root/"file_source.txt"
    if not file_path.exists():
        file_path.touch()
    gen_tasks1 = fetch_tasks(FileSource(str(file_path)))
    gen_tasks2 = fetch_tasks(GeneratorSource(2,seed=2))
    gen_tasks3 = fetch_tasks(FakeApiSource("https://example.com"))
    #l_tasks3=list(gen_tasks3.get_tasks())
    #l_tasks3[0].priority = 10
    q1=TaskQueue(gen_tasks1)
    q2 = TaskQueue(gen_tasks2)
    q3=TaskQueue(gen_tasks3)
    for i in q1:
        print(i)
    print(list(q2))
    print(sum(task.priority for task in q3))
if __name__ == "__main__":
    main()
