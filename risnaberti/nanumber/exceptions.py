# risnaberti/nanumber/exceptions.py
class NanumberError(Exception):
    """Base exception for all Nanumber errors"""
    pass

class TemplateError(NanumberError):
    """Raised when invalid placeholder used in template"""
    pass

class StorageError(NanumberError):
    """Raised when storage operation fails"""
    pass

class TemplateNotFoundError(NanumberError):
    """Raised when template key not found in templates dict"""
    pass