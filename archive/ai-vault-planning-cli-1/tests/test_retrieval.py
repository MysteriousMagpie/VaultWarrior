import pytest
from ai_vault_cli.retrieval.store import Store
from ai_vault_cli.retrieval.ranker import Ranker

def test_store_initialization():
    store = Store()
    assert store is not None

def test_store_add_and_retrieve():
    store = Store()
    item = {"id": 1, "content": "Test content"}
    store.add(item)
    retrieved = store.retrieve(1)
    assert retrieved == item

def test_ranker_initialization():
    ranker = Ranker()
    assert ranker is not None

def test_ranker_ranking():
    ranker = Ranker()
    items = [{"id": 1, "score": 10}, {"id": 2, "score": 5}]
    ranked = ranker.rank(items)
    assert ranked[0]["id"] == 1
    assert ranked[1]["id"] == 2