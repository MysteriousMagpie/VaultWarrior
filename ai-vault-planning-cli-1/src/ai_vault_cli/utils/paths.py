def get_vault_path(vault_name):
    """Return the full path to the specified vault."""
    import os
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "Vaults", vault_name)

def get_daily_note_path(vault_path):
    """Return the path to the daily note in the specified vault."""
    return os.path.join(vault_path, "daily", "daily_note.md")

def get_thread_path(vault_path, thread_slug):
    """Return the path to a specific thread file in the vault."""
    return os.path.join(vault_path, "threads", f"{thread_slug}.md")

def get_index_path(vault_path):
    """Return the path to the index file for the specified vault."""
    return os.path.join(vault_path, "_ai", "index.json")

def get_config_path(vault_path):
    """Return the path to the configuration file for the specified vault."""
    return os.path.join(vault_path, "_ai", "config.yaml")