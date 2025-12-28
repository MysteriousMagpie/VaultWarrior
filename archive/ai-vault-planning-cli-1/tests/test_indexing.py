import pytest
from ai_vault_cli.indexing.embeddings import create_embeddings
from ai_vault_cli.indexing.parser import parse_markdown
from ai_vault_cli.indexing.crawler import crawl_vault

def test_crawl_vault():
    vault_path = "path/to/sample/vault"
    files = crawl_vault(vault_path)
    assert isinstance(files, list)
    assert all(isinstance(file, str) for file in files)

def test_parse_markdown():
    sample_markdown = "# Sample Note\nThis is a sample note."
    parsed_content = parse_markdown(sample_markdown)
    assert "Sample Note" in parsed_content
    assert "This is a sample note." in parsed_content

def test_create_embeddings():
    sample_text = "This is a sample text for embedding."
    embeddings = create_embeddings(sample_text)
    assert isinstance(embeddings, list)
    assert len(embeddings) > 0  # Ensure embeddings are created

def test_indexing_integration():
    vault_path = "path/to/sample/vault"
    files = crawl_vault(vault_path)
    for file in files:
        content = parse_markdown(file)
        embeddings = create_embeddings(content)
        assert embeddings is not None  # Ensure embeddings are created for each file