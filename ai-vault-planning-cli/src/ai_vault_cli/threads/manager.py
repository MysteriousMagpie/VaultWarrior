from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Thread:
    slug: str
    content: str

class ThreadManager:
    def __init__(self, vault_path: str | None = None):
        self._threads: dict[str, Thread] = {}

    def create_thread(self, slug: str, content: str) -> Thread:
        t = Thread(slug=slug, content=content)
        self._threads[slug] = t
        return t

    def get_thread(self, slug: str) -> Optional[Thread]:
        return self._threads.get(slug)

    def update_thread(self, slug: str, new_content: str) -> None:
        if slug in self._threads:
            self._threads[slug].content = new_content

    def delete_thread(self, slug: str) -> None:
        self._threads.pop(slug, None)

    def list_threads(self) -> List[Thread]:
        return list(self._threads.values())