from typing import Optional


class ArraySizeError(Exception):
    """
    Array size errors custom exception
    """

    def __init__(self, message: str):
        super().__init__(message)


class CharArrayError(Exception):
    def __init__(self, message: Optional[str] = None):
        default_message = 'CHAR cannot be used as an array like this. Use primitives.CharArray class instead'
        super().__init__(message or default_message)
