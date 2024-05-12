import json
from typing import List
from pathlib import Path

from .models import Task


class TaskManager:
    def __init__(self, file_path: Path) -> None:
        self.content: List[Task] = []
        self._file_path = file_path

        if file_path.exists():
            self.content = json.loads(file_path.read_text("utf-8"))
        else:
            self.save()

    def save(self) -> None:
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(self.content, f, indent=4, ensure_ascii=False)

    def add(self, content: Task) -> None:
        self.content.append(content)
        self.save()
