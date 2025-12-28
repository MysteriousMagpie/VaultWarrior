from typing import List, Dict
import os

class ThreadManager:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.threads_dir = os.path.join(vault_path, 'threads')
        self.ensure_threads_directory()

    def ensure_threads_directory(self):
        if not os.path.exists(self.threads_dir):
            os.makedirs(self.threads_dir)

    def create_thread(self, slug: str, content: str) -> str:
        thread_file_path = os.path.join(self.threads_dir, f"{slug}.md")
        with open(thread_file_path, 'w') as thread_file:
            thread_file.write(content)
        return thread_file_path

    def list_threads(self) -> List[str]:
        return [f for f in os.listdir(self.threads_dir) if f.endswith('.md')]

    def read_thread(self, slug: str) -> str:
        thread_file_path = os.path.join(self.threads_dir, f"{slug}.md")
        if os.path.exists(thread_file_path):
            with open(thread_file_path, 'r') as thread_file:
                return thread_file.read()
        else:
            raise FileNotFoundError(f"Thread '{slug}' not found.")

    def delete_thread(self, slug: str) -> None:
        thread_file_path = os.path.join(self.threads_dir, f"{slug}.md")
        if os.path.exists(thread_file_path):
            os.remove(thread_file_path)
        else:
            raise FileNotFoundError(f"Thread '{slug}' not found.")

    def update_thread(self, slug: str, new_content: str) -> None:
        thread_file_path = os.path.join(self.threads_dir, f"{slug}.md")
        if os.path.exists(thread_file_path):
            with open(thread_file_path, 'w') as thread_file:
                thread_file.write(new_content)
        else:
            raise FileNotFoundError(f"Thread '{slug}' not found.")