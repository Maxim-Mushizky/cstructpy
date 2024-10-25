import struct
from typing import Any, Optional, Sequence, Self
from abc import ABC

from .exceptions import ArraySizeError, CharArrayError


# Base primitive type class (same as before)
class PrimitiveType(ABC):
    """
    Abstract base class for primitive types that defines methods for validation, packing,
    and unpacking binary data.

    Attributes:
        _format_char (str): The format character used by the `struct` module for packing/unpacking.
        _min_value (int, optional): The minimum allowable value for the type.
        _max_value (int, optional): The maximum allowable value for the type.
        _size (int): The size of the type in bytes.
    """

    def __init__(self, format_char: str = '',
                 min_value: Optional[int] = None,
                 max_value: Optional[int] = None,
                 size: int = 0
                 ) -> None:
        """
        Initializes a PrimitiveType with the given format character, optional min/max values, and size.

        Args:
            format_char (str): Format character for the type (e.g., 'i', 'f').
            min_value (int, optional): Minimum value allowed (for integer types).
            max_value (int, optional): Maximum value allowed (for integer types).
            size (int, optional): Size of the type in bytes.
        """
        self._format_char = format_char
        self._min_value = min_value
        self._max_value = max_value
        self._size = size

    @property
    def format_char(self):
        return self._format_char

    @property
    def min_value(self):
        return self._min_value

    @property
    def max_value(self):
        return self._max_value

    @property
    def size(self):
        return self._size

    def __class_getitem__(cls, array_size: int) -> Self:
        """
        Intercepts the [] operator, returning a new class that represents an array of this type.

        Args:
            array_size (int): The size of the array.

        Returns:
            PrimitiveType: The instantiated class with augmented format_char and size to represent array
        """
        if array_size == 0:
            raise ArraySizeError('error: size of array is zero')

        if array_size < 0:
            raise ArraySizeError('error: size of array is negative')

        _cls_instance = cls()
        _cls_instance._size *= array_size
        _cls_instance._format_char = f'{array_size}{_cls_instance._format_char}'

        return _cls_instance

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
        if isinstance(value, Sequence):
            if len(self._format_char) <= 1:
                raise ArraySizeError(f"Array of length {len(value)} provided but expected a single value")
            if (expected_val := int(self.format_char[:-1])) != len(value):
                raise ArraySizeError(f"Expected array size of {expected_val}. Got {len(value)} instead")
            return all([self._validate_for_single_value(v) for v in value])
        return self._validate_for_single_value(value)

    def _validate_for_single_value(self, value: Any) -> bool:
        if self._min_value is not None and value < self._min_value:
            raise ValueError(f"Value {value} is less than minimum {self._min_value}")
        if self._max_value is not None and value > self._max_value:
            raise ValueError(f"Value {value} is greater than maximum {self._max_value}")
        return True

    def pack(self, value: Any) -> bytes:
        self.validate(value)
        if isinstance(value, Sequence):
            return struct.pack(self._format_char, *value)
        return struct.pack(self._format_char, value)

    def unpack(self, data: bytes) -> Any:
        unpacked_object = struct.unpack(self._format_char, data)
        if len(unpacked_object) == 1:
            return unpacked_object[0]
        return unpacked_object


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


# ====== Special dtypes ======

# Floating point types
class FLOAT(PrimitiveType):
    def __init__(self):
        super().__init__('f', size=4)

    def validate(self, value: Any) -> bool:
        # For sequence
        if isinstance(value, Sequence):
            if len(self._format_char) <= 1:
                raise ArraySizeError(f"Array of length {len(value)} provided but expected a single value")
            for i, v in enumerate(value):
                if not isinstance(v, (int, float)):
                    raise ValueError(f"FLOAT at index {i} isn't DOUBLE, but {type(v)} instead")

        # For single case
        elif not isinstance(value, (int, float)):
            raise ValueError("FLOAT value must be a number")
        return True


class DOUBLE(PrimitiveType):
    def __init__(self):
        super().__init__('d', size=8)

    def validate(self, value: Any) -> bool:
        # For sequence
        if isinstance(value, Sequence):
            if len(self._format_char) <= 1:
                raise ArraySizeError(f"Array of length {len(value)} provided but expected a single value")
            for i, v in enumerate(value):
                if not isinstance(v, (int, float)):
                    raise ArraySizeError(f"Value at index {i} isn't DOUBLE, but {type(v)} instead")

        # For single case
        elif not isinstance(value, (int, float)):
            raise ValueError("DOUBLE value must be a number")
        return True


# Character types
class CHAR(PrimitiveType):
    def __init__(self):
        super().__init__('c', size=1)

    def __class_getitem__(cls, item):
        raise CharArrayError()

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
        # For sequence
        if isinstance(value, Sequence):
            if len(self._format_char) <= 1:
                raise ArraySizeError(f"Array of length {len(value)} provided but expected a single value")

            for i, v in enumerate(value):
                if not isinstance(v, bool):
                    raise ValueError(f"Value at index {i} isn't BOOL, but {type(v)} instead")
        # For single case
        elif not isinstance(value, bool):
            raise ValueError("BOOL value must be True or False")
        return True


# Padding type (for alignment)
class PADDING(PrimitiveType):
    def __init__(self, size: int):
        super().__init__(f'{size}x', size=size)

    def validate(self, value: Any) -> bool:
        return True

    def pack(self, value: Any = None) -> bytes:
        return b'\x00' * self._size

    def unpack(self, data: bytes) -> None:
        return None
