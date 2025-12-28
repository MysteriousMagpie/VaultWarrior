from pathlib import Path
import click
from ai_vault_cli.utils.logging import logger
from ai_vault_cli.vault.daily import append_to_daily_note

@click.command()
@click.argument('text')
@click.option('--write', is_flag=True, help='Write the capture to the daily note.')
def capture(text, write):
    """Capture quick notes and optionally write them to the daily note."""
    logger.info(f'Capturing text: {text}')
    
    if write:
        append_to_daily_note(text)
        logger.info('Text captured and written to the daily note.')
    else:
        logger.info('Text captured but not written to the daily note.')