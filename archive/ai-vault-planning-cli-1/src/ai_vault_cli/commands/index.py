from ai_vault_cli.indexing.crawler import crawl_markdown_files
from ai_vault_cli.indexing.parser import parse_markdown_files
from ai_vault_cli.indexing.embeddings import create_embeddings
from ai_vault_cli.utils.logging import log_info, log_error

def index_vault(vault_path):
    log_info(f"Starting indexing for vault at: {vault_path}")
    
    try:
        # Step 1: Crawl markdown files
        markdown_files = crawl_markdown_files(vault_path)
        log_info(f"Found {len(markdown_files)} markdown files.")

        # Step 2: Parse markdown files
        parsed_data = parse_markdown_files(markdown_files)
        log_info("Markdown files parsed successfully.")

        # Step 3: Create embeddings
        embeddings = create_embeddings(parsed_data)
        log_info("Embeddings created successfully.")

        # Here you would typically save the embeddings to a storage solution
        # For example, saving to a FAISS index or similar

        log_info("Indexing completed successfully.")
    except Exception as e:
        log_error(f"An error occurred during indexing: {e}")