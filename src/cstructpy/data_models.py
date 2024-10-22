from typing import get_type_hints, Any, Dict

from src.cstructpy.primitives import PrimitiveType, BOOL, CHAR, CHAR_ARRAY, INT8, U_INT8, INT16, U_INT16, INT32, \
    U_INT32, INT64, U_INT64, FLOAT, DOUBLE


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


def example_usage():
    class CompleteExample(GenericStruct):
        bool_val: BOOL
        char_val: CHAR
        string_val: CHAR_ARRAY(10)
        int8_val: INT8
        uint8_val: U_INT8
        int16_val: INT16
        uint16_val: U_INT16
        int32_val: INT32
        uint32_val: U_INT32
        int64_val: INT64
        uint64_val: U_INT64
        float_val: FLOAT
        double_val: DOUBLE

    # Create instance
    example = CompleteExample(
        bool_val=True,
        char_val='A',
        string_val="Hello",
        int8_val=-100,
        uint8_val=200,
        int16_val=-30000,
        uint16_val=60000,
        int32_val=-2000000000,
        uint32_val=4000000000,
        int64_val=-9000000000000000000,
        uint64_val=18000000000000000000,
        float_val=3.14,
        double_val=3.14159265359
    )

    # Pack to bytes
    packed = example.pack()
    print(packed)
    print(f"Packed size: {len(packed)} bytes")

    # Unpack from bytes
    unpacked = CompleteExample.unpack(packed)
    print(f"Unpacked values: {unpacked.to_dict()}")

if __name__ == '__main__':
    example_usage()