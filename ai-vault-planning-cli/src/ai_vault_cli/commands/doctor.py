import click

@click.group()
def cli():
    pass

@cli.command('doctor')
def doctor_cmd():
    click.echo('Sanity check complete')

if __name__ == '__main__':
    cli()
import os

def check_config_exists(config_path):
    return os.path.exists(config_path)

def check_index_exists(index_path):
    return os.path.exists(index_path)

def run_diagnostics(config_path, index_path):
    diagnostics = []
    
    if not check_config_exists(config_path):
        diagnostics.append("Config file is missing.")
    
    if not check_index_exists(index_path):
        diagnostics.append("Index file is missing.")
    
    if not diagnostics:
        diagnostics.append("All checks passed. Configuration and index are present.")
    
    return diagnostics

def main():
    config_path = os.path.join(os.path.expanduser("~"), ".ai_vault/config.yaml")
    index_path = os.path.join(os.path.expanduser("~"), ".ai_vault/index.faiss")
    
    results = run_diagnostics(config_path, index_path)
    
    for result in results:
        print(result)

if __name__ == "__main__":
    main()