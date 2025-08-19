class VaultError(Exception):
    """Base class for exceptions in the vault planning CLI."""
    pass

class ConfigurationError(VaultError):
    """Exception raised for errors in the configuration."""
    pass

class IndexingError(VaultError):
    """Exception raised for errors during indexing."""
    pass

class RetrievalError(VaultError):
    """Exception raised for errors during retrieval."""
    pass

class ThreadError(VaultError):
    """Exception raised for errors related to thread management."""
    pass

class ChatError(VaultError):
    """Exception raised for errors during chat interactions."""
    pass

class CaptureError(VaultError):
    """Exception raised for errors during note capturing."""
    pass

class PlanningError(VaultError):
    """Exception raised for errors during planning."""
    pass

class DoctorError(VaultError):
    """Exception raised for errors during sanity checks."""
    pass