import os
import yaml

def init_vault(vault_path):
    # Create the vault directory if it doesn't exist
    if not os.path.exists(vault_path):
        os.makedirs(vault_path)

    # Create the config directory and the config.yaml file
    config_dir = os.path.join(vault_path, '_ai')
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'config.yaml')
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            yaml.dump({'vault_path': vault_path}, f)

    # Create thread and daily directories
    os.makedirs(os.path.join(vault_path, 'threads'), exist_ok=True)
    os.makedirs(os.path.join(vault_path, 'daily'), exist_ok=True)

    print(f"Initialized AI Vault at {vault_path}")