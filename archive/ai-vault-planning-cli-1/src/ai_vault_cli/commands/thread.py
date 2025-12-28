from typing import Dict, Any
from ai_vault_cli.threads.manager import ThreadManager

def create_thread(slug: str, vault_path: str, seed: str) -> None:
    """Create a new thread with the given slug and seed text."""
    thread_manager = ThreadManager(vault_path)
    thread_manager.create_thread(slug, seed)

def list_threads(vault_path: str) -> None:
    """List all threads in the specified vault."""
    thread_manager = ThreadManager(vault_path)
    threads = thread_manager.list_threads()
    for thread in threads:
        print(thread)

def delete_thread(slug: str, vault_path: str) -> None:
    """Delete the specified thread."""
    thread_manager = ThreadManager(vault_path)
    thread_manager.delete_thread(slug)

def update_thread(slug: str, vault_path: str, updates: Dict[str, Any]) -> None:
    """Update the specified thread with new information."""
    thread_manager = ThreadManager(vault_path)
    thread_manager.update_thread(slug, updates)