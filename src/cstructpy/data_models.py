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
        Initializes the GenericStruct instance, setting up fields based on type hints.
        Only enforces defaults if explicitly provided in subclasses.
        """
        self._type_hints = get_type_hints(self.__class__)

        # Identify and set fields with explicit defaults in the subclass
        for field_name, field_type in self._type_hints.items():
            # Check if field_type is a subclass of GenericStruct
            if isinstance(field_type, type) and issubclass(field_type, GenericStruct):
                setattr(self, f'_{field_name}_type', field_type)
            # Check if it's a primitive type
            elif isinstance(field_type, type) and issubclass(field_type, PrimitiveType):
                setattr(self, f'_{field_name}_type', field_type())
            else:
                setattr(self, f'_{field_name}_type', field_type)

            # Check if the field has a default; enforce if set in the subclass or passed in kwargs
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
            elif hasattr(self.__class__, field_name):  # Enforce default if defined in subclass
                setattr(self, field_name, getattr(self.__class__, field_name))

        for key, value in kwargs.items():
            if key not in self._type_hints:
                raise ValueError(f"Unknown field: {key}")
            setattr(self, key, value)

    def get_field_size(self, field_type) -> int:
        """
        Calculate the size of a field, whether it's a primitive type or a nested struct.

        Args:
            field_type: The type of the field (either PrimitiveType instance or GenericStruct class)

        Returns:
            int: The size in bytes of the field
        """
        if isinstance(field_type, type) and issubclass(field_type, GenericStruct):
            # For nested structs, create a temporary instance and calculate total size
            temp_instance = field_type()
            return sum(self.get_field_size(getattr(temp_instance, f'_{name}_type'))
                       for name in temp_instance._type_hints)
        else:
            # For primitive types, return their size directly
            return field_type.size

    def __setattr__(self, name: str, value: Any):
        # Bypass type enforcement for private attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        # Validate type only for fields with defaults or explicitly passed fields
        if name in getattr(self, '_type_hints', {}):
            type_instance = getattr(self, f'_{name}_type')

            # Handle nested GenericStruct
            if isinstance(type_instance, type) and issubclass(type_instance, GenericStruct):
                if not isinstance(value, type_instance):
                    raise TypeError(f"Expected {type_instance.__name__}, got {type(value).__name__}")
            else:
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

            # Handle nested GenericStruct
            if isinstance(type_instance, type) and issubclass(type_instance, GenericStruct):
                result += value.pack()
            else:
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

            # Handle nested GenericStruct
            if isinstance(type_instance, type) and issubclass(type_instance, GenericStruct):
                field_size = temp_instance.get_field_size(type_instance)
                field_data = data[offset:offset + field_size]
                kwargs[field_name] = type_instance.unpack(field_data)
            else:
                field_size = type_instance.size
                field_data = data[offset:offset + field_size]
                kwargs[field_name] = type_instance.unpack(field_data)

            offset += field_size

        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the structure to a dictionary with field names as keys and their values.
        Handles nested structures recursively.

        Returns:
            dict: A dictionary representation of the structure.
        """
        result = {}
        for field_name in self._type_hints:
            value = getattr(self, field_name)
            if isinstance(value, GenericStruct):
                result[field_name] = value.to_dict()
            else:
                result[field_name] = value
        return result

    def __eq__(self, other) -> bool:
        if isinstance(other, GenericStruct):
            return self.to_dict() == other.to_dict()
        return False

    def __repr__(self):
        """
        Provides a string representation of the instance with all user-defined attributes and their values.

        Returns:
            str: A string showing the class name and user-defined attribute names and values.
        """
        # Collect all attributes that don't start with an underscore
        attributes = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        # Format the attributes for display
        attr_str = ', '.join(f"{k}={v!r}" for k, v in attributes.items())
        return f"{self.__class__.__name__}({attr_str})"
