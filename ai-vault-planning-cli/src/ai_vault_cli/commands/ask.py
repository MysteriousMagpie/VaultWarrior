import click

@click.command()
@click.argument('question')
def ask(question):
    """Ask a question and retrieve an answer from the AI."""
    # Simplified implementation for tests
    answer = f"Answer: (stub) {question}"
    click.echo(answer)

    # Optionally write the answer to the thread