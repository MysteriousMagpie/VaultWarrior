from typing import Dict, Any

class VaultMetadata:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.metadata_file = f"{vault_path}/_ai/metadata.json"
        self.metadata = self.load_metadata()

    def load_metadata(self) -> Dict[str, Any]:
        try:
            with open(self.metadata_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def save_metadata(self) -> None:
        with open(self.metadata_file, 'w') as file:
            json.dump(self.metadata, file, indent=4)

    def update_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
        self.save_metadata()

    def get_metadata(self, key: str) -> Any:
        return self.metadata.get(key, None)