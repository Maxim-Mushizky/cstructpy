import struct
from typing import Any
from abc import ABC


# Base primitive type class (same as before)
class PrimitiveType(ABC):
    """
    Abstract base class for primitive types that defines methods for validation, packing,
    and unpacking binary data.

    Attributes:
        format_char (str): The format character used by the `struct` module for packing/unpacking.
        min_value (int, optional): The minimum allowable value for the type.
        max_value (int, optional): The maximum allowable value for the type.
        size (int): The size of the type in bytes.
    """

    def __init__(self, format_char: str,
                 min_value: int = None,
                 max_value: int = None,
                 size: int = None
                 ) -> None:
        """
        Initializes a PrimitiveType with the given format character, optional min/max values, and size.

        Args:
            format_char (str): Format character for the type (e.g., 'i', 'f').
            min_value (int, optional): Minimum value allowed (for integer types).
            max_value (int, optional): Maximum value allowed (for integer types).
            size (int, optional): Size of the type in bytes.
        """
        self.format_char = format_char
        self.min_value = min_value
        self.max_value = max_value
        self.size = size

    def validate(self, value: Any) -> bool:
        """
        Validates the given value against the type's constraints (min/max).

        Args:
            value (Any): The value to validate.

        Raises:
            ValueError: If the value does not meet the type's constraints.

        Returns:
            bool: True if the value is valid.
        """
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Value {value} is less than minimum {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Value {value} is greater than maximum {self.max_value}")
        return True

    def pack(self, value: Any) -> bytes:
        self.validate(value)
        return struct.pack(self.format_char, value)

    def unpack(self, data: bytes) -> Any:
        return struct.unpack(self.format_char, data)[0]


# Integer types
class INT8(PrimitiveType):
    def __init__(self):
        super().__init__('b', min_value=-128, max_value=127, size=1)


class UINT8(PrimitiveType):
    def __init__(self):
        super().__init__('B', min_value=0, max_value=255, size=1)


class INT16(PrimitiveType):
    def __init__(self):
        super().__init__('h', min_value=-32768, max_value=32767, size=2)


class UINT16(PrimitiveType):
    def __init__(self):
        super().__init__('H', min_value=0, max_value=65535, size=2)


class INT32(PrimitiveType):
    def __init__(self):
        super().__init__('i', min_value=-2147483648, max_value=2147483647, size=4)


class UINT32(PrimitiveType):
    def __init__(self):
        super().__init__('I', min_value=0, max_value=4294967295, size=4)


class INT64(PrimitiveType):
    def __init__(self):
        super().__init__('q', min_value=-9223372036854775808, max_value=9223372036854775807, size=8)


class UINT64(PrimitiveType):
    def __init__(self):
        super().__init__('Q', min_value=0, max_value=18446744073709551615, size=8)


# Floating point types
class FLOAT(PrimitiveType):
    def __init__(self):
        super().__init__('f', size=4)

    def validate(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            raise ValueError("FLOAT value must be a number")
        return True


class DOUBLE(PrimitiveType):
    def __init__(self):
        super().__init__('d', size=8)

    def validate(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            raise ValueError("DOUBLE value must be a number")
        return True


# Character types
class CHAR(PrimitiveType):
    def __init__(self):
        super().__init__('c', size=1)

    def validate(self, value: Any) -> bool:
        if not isinstance(value, (str, bytes)) or len(str(value)) != 1:
            raise ValueError("CHAR must be a single character")
        return True

    def pack(self, value: Any) -> bytes:
        self.validate(value)
        if isinstance(value, str):
            return value.encode('ascii')
        return value

    def unpack(self, data: bytes) -> str:
        return super().unpack(data).decode('ascii')


class CharArray(PrimitiveType):
    def __init__(self, length: int):
        super().__init__(f'{length}s', size=length)
        self.length = length

    def validate(self, value: Any) -> bool:
        if not isinstance(value, (str, bytes)):
            raise ValueError("CHAR_ARRAY value must be string or bytes")
        if len(value) > self.length:
            raise ValueError(f"String length exceeds {self.length} characters")
        return True

    def pack(self, value: Any) -> bytes:
        self.validate(value)
        if isinstance(value, str):
            return value.encode('ascii').ljust(self.length, b'\x00')
        return value.ljust(self.length, b'\x00')

    def unpack(self, data: bytes) -> str:
        result = super().unpack(data)
        if isinstance(result, bytes):
            # Remove null padding and decode
            return result.rstrip(b'\x00').decode('ascii')
        return result


# Boolean type
class BOOL(PrimitiveType):
    def __init__(self):
        super().__init__('?', size=1)

    def validate(self, value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValueError("BOOL value must be True or False")
        return True


# Padding type (for alignment)
class PADDING(PrimitiveType):
    def __init__(self, size: int):
        super().__init__(f'{size}x', size=size)

    def validate(self, value: Any) -> bool:
        return True

    def pack(self, value: Any = None) -> bytes:
        return b'\x00' * self.size

    def unpack(self, data: bytes) -> None:
        return None
