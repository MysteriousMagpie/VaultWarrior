import click
from ai_vault_cli.commands import init, index, thread, ask, chat, capture, plan, doctor

@click.group()
def cli():
    pass

# Register subcommands from each module's group
for mod in (init, index, thread, ask, chat, capture, plan, doctor):
    if hasattr(mod, 'cli'):
        for cmd in getattr(mod, 'cli').commands.values():  # type: ignore
            cli.add_command(cmd)

if __name__ == '__main__':
    cli()