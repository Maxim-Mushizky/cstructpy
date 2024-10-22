from typing import get_type_hints, Any, Dict
from .primitives import PrimitiveType

class GenericStruct:
    def __init__(self, **kwargs):
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
        result = b''
        for field_name in self._type_hints:
            value = getattr(self, field_name)
            type_instance = getattr(self, f'_{field_name}_type')
            result += type_instance.pack(value)
        return result

    @classmethod
    def unpack(cls, data: bytes):
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
        return {
            field_name: getattr(self, field_name)
            for field_name in self._type_hints
        }
