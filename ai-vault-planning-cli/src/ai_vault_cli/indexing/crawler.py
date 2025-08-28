# Crawler for Markdown Files in the Vault

import os
import glob
from typing import List

def crawl_markdown_files(vault_path):
    """Crawl through the specified vault path and return a list of markdown files."""
    markdown_files = glob.glob(os.path.join(vault_path, '**', '*.md'), recursive=True)
    return markdown_files

def read_markdown_file(file_path):
    """Read the contents of a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def crawl_and_read(vault_path):
    """Crawl markdown files in the vault and read their contents."""
    files = crawl_markdown_files(vault_path)
    contents = {}
    for file in files:
        contents[file] = read_markdown_file(file)
    return contents

def crawl_vault(vault_path: str) -> List[str]:
    """Test-facing wrapper returning list of markdown file paths (strings)."""
    return crawl_markdown_files(vault_path)