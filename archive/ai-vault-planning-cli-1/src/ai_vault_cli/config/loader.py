import os
import yaml

def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    return config

def get_default_config():
    return {
        'vault_path': '',
        'api_key': '',
        'indexing': {
            'enabled': True,
            'watch': False
        },
        'logging': {
            'level': 'INFO'
        }
    }