import click
from ai_vault_cli.llm.openai_provider import OpenAIProvider
from ai_vault_cli.retrieval.store import RetrievalStore
from ai_vault_cli.utils.logging import logger

@click.command()
@click.argument('question')
@click.option('--vault-path', required=True, help='Path to the markdown vault.')
@click.option('--write', is_flag=True, help='Append the answer to the thread.')
def ask(question, vault_path, write):
    """Ask a question and retrieve an answer from the AI."""
    logger.info(f"Asking question: {question} from vault: {vault_path}")

    # Initialize OpenAI provider and retrieval store
    openai_provider = OpenAIProvider()
    retrieval_store = RetrievalStore(vault_path)

    # Retrieve relevant context from the vault
    context = retrieval_store.retrieve_context(question)

    # Get the answer from the AI
    answer = openai_provider.get_answer(question, context)

    # Print the answer
    click.echo(answer)

    # Optionally write the answer to the thread
    if write:
        # Logic to append the answer to the thread
        pass