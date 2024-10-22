from typing import get_type_hints, Any, Dict
from .primitives import PrimitiveType


class GenericStruct:
    """
    A base class for structured data that provides methods to pack and unpack binary data
    and to dynamically create fields based on type hints.

    Attributes:
        _type_hints (dict): Type hints for the class attributes, used for field validation and packing.
    """

    def __init__(self, **kwargs):
        """
        Initializes the GenericStruct instance and sets default types for all fields based on type hints.
        Accepts keyword arguments for field values.

        Args:
            **kwargs: Keyword arguments corresponding to the fields and their values.

        Raises:
            ValueError: If a field name does not exist in the class type hints.
        """
        self._type_hints = get_type_hints(self.__class__)

        for field_name, field_type in self._type_hints.items():
            if isinstance(field_type, type) and issubclass(field_type, PrimitiveType):
                setattr(self, f'_{field_name}_type', field_type())
            else:
                setattr(self, f'_{field_name}_type', field_type)

        for key, value in kwargs.items():
            if key not in self._type_hints:
                raise ValueError(f"Unknown field: {key}")
            setattr(self, key, value)

    def __setattr__(self, name: str, value: Any):
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        if name not in getattr(self, '_type_hints', {}):
            super().__setattr__(name, value)
            return

        type_instance = getattr(self, f'_{name}_type')
        type_instance.validate(value)
        super().__setattr__(name, value)

    def pack(self) -> bytes:
        """
        Packs the structure's fields into a binary representation using the defined types.

        Returns:
            bytes: The packed binary data for the structure.
       """
        result = b''
        for field_name in self._type_hints:
            value = getattr(self, field_name)
            type_instance = getattr(self, f'_{field_name}_type')
            result += type_instance.pack(value)
        return result

    @classmethod
    def unpack(cls, data: bytes):
        """
        Unpacks binary data into a structure instance by reading field values according to their types.

        Args:
            data (bytes): The binary data to unpack.

        Returns:
            GenericStruct: An instance of the class with field values set from the binary data.
        """
        offset = 0
        kwargs = {}

        temp_instance = cls()

        for field_name in temp_instance._type_hints:
            type_instance = getattr(temp_instance, f'_{field_name}_type')
            field_size = type_instance.size
            field_data = data[offset:offset + field_size]
            kwargs[field_name] = type_instance.unpack(field_data)
            offset += field_size

        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the structure to a dictionary with field names as keys and their values.

        Returns:
            dict: A dictionary representation of the structure.
        """
        return {
            field_name: getattr(self, field_name)
            for field_name in self._type_hints
        }
