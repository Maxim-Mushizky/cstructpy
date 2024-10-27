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
            # Define the field type for packing/unpacking
            if isinstance(field_type, type) and issubclass(field_type, PrimitiveType):
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

    def __setattr__(self, name: str, value: Any):
        # Bypass type enforcement for private attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        # Validate type only for fields with defaults or explicitly passed fields
        if name in getattr(self, '_type_hints', {}):
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

    def __eq__(self, other) -> bool:
        if isinstance(other, GenericStruct):
            # Get dictionaries of attributes for both instances
            self_attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('__')}
            other_attrs = {k: v for k, v in other.__dict__.items() if not k.startswith('__')}

            # for self
            for k, v in self_attrs.items():
                if '_type' in k and k != '_type_hints':  # Update only to the class and ignore type_hints
                    self_attrs[k] = v.__class__

            # for other
            for k, v in other_attrs.items():
                if '_type' in k and k != '_type_hints':  # Update only to the class and ignore type_hints
                    other_attrs[k] = v.__class__

            # Compare user-defined attributes
            return self_attrs == other_attrs
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
