import pytest
from ai_vault_cli.threads.manager import ThreadManager

@pytest.fixture
def thread_manager():
    return ThreadManager()

def test_create_thread(thread_manager):
    slug = "test-thread"
    thread = thread_manager.create_thread(slug, "Test thread content")
    assert thread.slug == slug
    assert thread.content == "Test thread content"

def test_get_thread(thread_manager):
    slug = "existing-thread"
    thread_manager.create_thread(slug, "Existing thread content")
    thread = thread_manager.get_thread(slug)
    assert thread is not None
    assert thread.content == "Existing thread content"

def test_update_thread(thread_manager):
    slug = "update-thread"
    thread_manager.create_thread(slug, "Initial content")
    thread_manager.update_thread(slug, "Updated content")
    thread = thread_manager.get_thread(slug)
    assert thread.content == "Updated content"

def test_delete_thread(thread_manager):
    slug = "delete-thread"
    thread_manager.create_thread(slug, "Content to be deleted")
    thread_manager.delete_thread(slug)
    thread = thread_manager.get_thread(slug)
    assert thread is None

def test_list_threads(thread_manager):
    thread_manager.create_thread("thread-1", "Content 1")
    thread_manager.create_thread("thread-2", "Content 2")
    threads = thread_manager.list_threads()
    assert len(threads) == 2
    assert "thread-1" in [t.slug for t in threads]
    assert "thread-2" in [t.slug for t in threads]