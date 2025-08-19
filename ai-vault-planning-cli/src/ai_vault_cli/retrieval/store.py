from typing import List, Dict

class RetrievalStore:
    def __init__(self):
        self.data = {}

    def add_entry(self, key: str, value: str) -> None:
        """Add a new entry to the store."""
        self.data[key] = value

    def get_entry(self, key: str) -> str:
        """Retrieve an entry from the store by key."""
        return self.data.get(key, None)

    def remove_entry(self, key: str) -> None:
        """Remove an entry from the store by key."""
        if key in self.data:
            del self.data[key]

    def list_entries(self) -> List[Dict[str, str]]:
        """List all entries in the store."""
        return [{"key": key, "value": value} for key, value in self.data.items()]