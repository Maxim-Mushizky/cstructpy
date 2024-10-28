import random

import pytest
from src.cstructpy.primitives import (
    BOOL, CHAR, CharArray,
    INT8, UINT8, INT16, UINT16, INT32, UINT32, INT64, UINT64,
    FLOAT, DOUBLE
)
from src.cstructpy import GenericStruct
from src.cstructpy import exceptions


class TestInt16Type:

    def test_valid_values(self, int16_struct):
        int16_obj = int16_struct(value=12345)
        assert int16_obj.value == 12345

        int16_obj.value = -12345
        assert int16_obj.value == -12345

    def test_invalid_values(self, int16_struct):
        int16_obj = int16_struct(value=12345)
        with pytest.raises(ValueError):
            int16_obj.value = 2 ** 15 + 1  # maximum val
        with pytest.raises(ValueError):
            int16_obj.value = - 2 ** 15 - 1  # minimum val


# Test primitive types
class TestBooleanType:
    def test_valid_values(self, bool_struct):
        s = bool_struct(value=True)
        assert s.value is True

        s.value = False
        assert s.value is False

    def test_invalid_values(self, bool_struct):
        s = bool_struct(value=True)
        with pytest.raises(ValueError):
            s.value = 1
        with pytest.raises(exceptions.ArraySizeError):
            s.value = "True"
        with pytest.raises(exceptions.ArraySizeError):
            s.value = b'348234809234809782634867234'

    def test_pack_unpack(self, bool_struct):
        s = bool_struct(value=True)
        packed = s.pack()
        assert len(packed) == 1

        unpacked = bool_struct.unpack(packed)
        assert unpacked.value is True


class TestCharType:
    def test_valid_values(self, char_struct):
        s = char_struct(value='A')
        assert s.value == 'A'

        s.value = 'Z'
        assert s.value == 'Z'

    def test_invalid_values(self, char_struct):
        with pytest.raises(ValueError, match="single character"):
            char_struct(value='AB')

        s = char_struct(value='A')
        with pytest.raises(ValueError):
            s.value = 123

    def test_pack_unpack(self, char_struct):
        s = char_struct(value='X')
        packed = s.pack()
        assert len(packed) == 1

        unpacked = char_struct.unpack(packed)
        assert unpacked.value == 'X'


class TestCharArrayType:
    def test_valid_values(self, string_struct):
        s = string_struct(value="Hello")
        assert s.value == "Hello"

        s.value = "Hi"  # Shorter string
        assert s.value == "Hi"

    def test_invalid_values(self, string_struct):
        with pytest.raises(ValueError, match="exceeds"):
            string_struct(value="Too Long")

        s = string_struct(value="Test")
        with pytest.raises(ValueError):
            s.value = 123

    def test_pack_unpack_with_padding(self, string_struct):
        s = string_struct(value="Hi")
        packed = s.pack()
        assert len(packed) == 5  # Full length including padding

        unpacked = string_struct.unpack(packed)
        assert unpacked.value == "Hi"  # Padding should be stripped


# Parametrized tests for numeric types
@pytest.mark.parametrize("type_class,min_val,max_val,size", [
    (INT8, -128, 127, 1),
    (UINT8, 0, 255, 1),
    (INT16, -32768, 32767, 2),
    (UINT16, 0, 65535, 2),
    (INT32, -2147483648, 2147483647, 4),
    (UINT32, 0, 4294967295, 4),
    (INT64, -9223372036854775808, 9223372036854775807, 8),
    (UINT64, 0, 18446744073709551615, 8)
])
class TestIntegerTypes:
    def test_valid_range(self, type_class, min_val, max_val, size):
        class NumStruct(GenericStruct):
            value: type_class

        s = NumStruct(value=0)
        s.value = min_val
        assert s.value == min_val
        s.value = max_val
        assert s.value == max_val

    def test_invalid_range(self, type_class, min_val, max_val, size):
        class NumStruct(GenericStruct):
            value: type_class

        s = NumStruct(value=0)
        with pytest.raises(ValueError):
            s.value = min_val - 1
        with pytest.raises(ValueError):
            s.value = max_val + 1

    def test_pack_unpack(self, type_class, min_val, max_val, size):
        class NumStruct(GenericStruct):
            value: type_class

        test_val = max_val // 2
        s = NumStruct(value=test_val)
        packed = s.pack()
        assert len(packed) == size

        unpacked = NumStruct.unpack(packed)
        assert unpacked.value == test_val


class TestFloatingTypes:
    @pytest.mark.parametrize("type_class,size,places", [
        (FLOAT, 4, 6),
        (DOUBLE, 8, 15)
    ])
    def test_pack_unpack_precision(self, type_class, size, places):
        class FloatStruct(GenericStruct):
            value: type_class

        test_val = 3.141592653589793
        s = FloatStruct(value=test_val)
        packed = s.pack()
        assert len(packed) == size

        unpacked = FloatStruct.unpack(packed)
        assert unpacked.value == pytest.approx(unpacked.value,
                                               rel=10 ** -places), f"Unequal values  at {places} precision"

    @pytest.mark.parametrize("type_class", [FLOAT, DOUBLE])
    def test_invalid_values(self, type_class):
        class FloatStruct(GenericStruct):
            value: type_class

        with pytest.raises(exceptions.ArraySizeError):
            FloatStruct(value="3.14")

        s = FloatStruct(value=1.0)
        with pytest.raises(exceptions.ArraySizeError):
            s.value = "invalid"


class TestComplexStructs:
    def test_mixed_struct_creation(self, mixed_struct):
        s = mixed_struct(
            bool_val=True,
            char_val='X',
            int16_val=-1234,
            float_val=3.14,
            string_val="Hello"
        )

        assert s.bool_val is True
        assert s.char_val == 'X'
        assert s.int16_val == -1234
        assert s.float_val == pytest.approx(3.14, rel=10 ** -6)
        assert s.string_val == "Hello"

    def test_mixed_struct_pack_unpack(self, mixed_struct):
        original = mixed_struct(
            bool_val=True,
            char_val='X',
            int16_val=-1234,
            float_val=3.14,
            string_val="Hello"
        )

        packed = original.pack()
        assert len(packed) == 18  # 1 + 1 + 2  + 4 + 10

        unpacked = mixed_struct.unpack(packed)
        assert unpacked.bool_val == original.bool_val
        assert unpacked.char_val == original.char_val
        assert unpacked.int16_val == original.int16_val
        assert unpacked.float_val == pytest.approx(unpacked.float_val, rel=10 ** (-6))
        assert unpacked.string_val == original.string_val


class TestErrorHandling:
    def test_invalid_field_name(self, mixed_struct):
        with pytest.raises(ValueError, match="Unknown field"):
            mixed_struct(invalid_field="value")

    def test_missing_required_field(self, mixed_struct):
        with pytest.raises(AttributeError):
            mixed_struct(bool_val=True).pack()  # Missing other required fields


class TestArrayCreation:

    def test_array_creation_for_primitives(self, arrays_struct_6):
        arrays_struct_obj = arrays_struct_6(
            bool_array_6=[True, False, False, True, False, False],
            int16_array_6=[1234, 23341, 12, 1451, 234, 11],
            float_array_6=[3.141592, 123.141592, -1233.141592, 13.141391, -1001.141592, 10000.141592],
            uint16_array_6=[1234, 43341, 12, 1451, 234, 11],
            uint32_array_6=[1234, 23341, 12, 1451, 234, 11],
            uint64_array_6=[1234, 23341, 12, 23123123, 234, 1844674407370955]
        )

        packed = arrays_struct_obj.pack()
        assert len(packed) == (1 + 2 + 4 + 2 + 4 + 8) * 6, "Checksum failed"

        arrays_struct_6_unpacked = arrays_struct_6.unpack(packed)

        assert list(arrays_struct_6_unpacked.bool_array_6) == arrays_struct_obj.bool_array_6
        assert list(arrays_struct_6_unpacked.int16_array_6) == arrays_struct_obj.int16_array_6
        assert list(arrays_struct_6_unpacked.uint16_array_6) == arrays_struct_obj.uint16_array_6
        assert list(arrays_struct_6_unpacked.uint32_array_6) == arrays_struct_obj.uint32_array_6
        assert list(arrays_struct_6_unpacked.uint64_array_6) == arrays_struct_obj.uint64_array_6

        # Check for float precision
        for u_val, val in zip(arrays_struct_6_unpacked.float_array_6, arrays_struct_obj.float_array_6):
            assert val == pytest.approx(u_val, rel=10 ** -6)

    def test_char_not_used_as_array(self):
        with pytest.raises(exceptions.CharArrayError):
            class BrokenCharArray(GenericStruct):
                char_array: CHAR[6]

    def test_array_length_fixed(self):
        class FixedArrayInt(GenericStruct):
            values: INT16[4]

        with pytest.raises(exceptions.ArraySizeError):
            FixedArrayInt(values=[1, 2, 3])
        with pytest.raises(exceptions.ArraySizeError):
            FixedArrayInt(values=[1, 2, 3, 3, 1])

        array_obj = FixedArrayInt(values=[1, 2, 3, 3])
        assert len(array_obj.values) == 4, "Array size isn't length expected of 4"


class TestClassDefaults:

    def test_default_creation(self):
        class MixedStruct(GenericStruct):
            bool_val: BOOL = True
            uint32_array: UINT32[4] = [1, 2, 3, 4]
            int32: INT32 = 324

        try:
            mixed_struct_obj = MixedStruct()
        except Exception as e:
            raise AssertionError(f"Object from mixed struct causes and exception, when it shouldn't. {e}")

        assert mixed_struct_obj.bool_val is True
        assert mixed_struct_obj.uint32_array == [1, 2, 3, 4]
        assert mixed_struct_obj.int32 == 324

        packed = mixed_struct_obj.pack()
        unpacked = mixed_struct_obj.unpack(packed)

        assert mixed_struct_obj.bool_val == unpacked.bool_val
        assert mixed_struct_obj.uint32_array == list(unpacked.uint32_array)
        assert mixed_struct_obj.int32 == unpacked.int32

    def test_defaults_raise_exceptions(self):

        with pytest.raises(ValueError):
            class MixedStruct(GenericStruct):
                bool_val: BOOL = 1
                uint32_array: UINT32[4] = [1, 2, 3, 4]
                int32: INT32 = 324

            MixedStruct()
        with pytest.raises(exceptions.ArraySizeError):
            class MixedStruct(GenericStruct):
                bool_val: BOOL = True
                uint32_array: UINT32[4] = [1, 2, 3]
                int32: INT32 = 324

            MixedStruct()

        with pytest.raises(ValueError):
            class MixedStruct(GenericStruct):
                bool_val: BOOL = True
                uint32_array: UINT32[4] = [1, 2, 3, 4]
                int16: INT16 = 2 ** 15

            MixedStruct()

    def test_variables_change_from_defaults(self):
        class MixedStruct(GenericStruct):
            bool_val: BOOL = True
            uint32_array: UINT32[4] = [1, 2, 3, 4]
            int32: INT32 = 324

        mixed_struct_obj = MixedStruct(bool_val=False)
        mixed_struct_obj.uint32_array = [12, 12, 12, 12]

        assert mixed_struct_obj.bool_val is False
        assert mixed_struct_obj.uint32_array == [12, 12, 12, 12]

        packed = mixed_struct_obj.pack()
        unpacked = mixed_struct_obj.unpack(packed)

        assert mixed_struct_obj.bool_val == unpacked.bool_val
        assert mixed_struct_obj.uint32_array == list(unpacked.uint32_array)
        assert mixed_struct_obj.int32 == unpacked.int32


class TestUtilities:
    def test_to_dict(self, mixed_struct):
        s = mixed_struct(
            bool_val=True,
            char_val='X',
            int16_val=-1234,
            float_val=3.14,
            string_val="Hello"
        )

        d = s.to_dict()
        assert d == {
            'bool_val': True,
            'char_val': 'X',
            'int16_val': -1234,
            'float_val': pytest.approx(3.14),
            'string_val': "Hello"
        }

    def test_padding_ignored_in_dict(self):
        class PaddedStruct(GenericStruct):
            value: INT16
            next_value: INT16

        s = PaddedStruct(value=1, next_value=2)
        d = s.to_dict()
        assert d == {'value': 1, 'next_value': 2}

    @pytest.mark.parametrize('value', [random.randint(int(-2 ** 15 + 1), int(2 ** 15 - 1)) for _ in range(10)])
    def test_equality_between_generic_structs(self, value, int16_struct):
        class LocalInt16Struct(GenericStruct):
            value: INT16

        int16_obj = int16_struct(value=value)
        local_int16_obj = LocalInt16Struct(value=value)
        assert int16_obj == local_int16_obj, "The objects should be equal"
        assert local_int16_obj == int16_obj, "The objects should be equal"

    def test_equality_for_complex_generic_struct(self, complex_struct):
        class LocalComplexStruct(GenericStruct):
            bool_val: BOOL
            char_val: CHAR
            int16_val: INT16
            float_val: FLOAT
            uint16_val: UINT16
            uint32_val: UINT32
            uint64_val: UINT64

        complex_obj = complex_struct(
            bool_val=True,
            char_val='X',
            int16_val=-1234,
            float_val=3.14,
            uint16_val=int(2 ** 16 - 1),
            uint32_val=int(2 ** 32 - 1),
            uint64_val=int(2 ** 64 - 1)
        )

        local_complex_struct = LocalComplexStruct(
            bool_val=True,
            char_val='X',
            int16_val=-1234,
            float_val=3.14,
            uint16_val=int(2 ** 16 - 1),
            uint32_val=int(2 ** 32 - 1),
            uint64_val=int(2 ** 64 - 1)
        )

        assert local_complex_struct == complex_obj, "The objects should be equal"
        assert complex_obj == local_complex_struct, "The objects should be equal"

    def test_inequality_between_char_array_generic_structs(self, string_struct):
        # Arrays in different memory locations, thus they shouldn't be equal
        class LocalStringStruct(GenericStruct):
            value: CharArray(5)

        string_obj = string_struct(value='yes')
        local_string_obj = LocalStringStruct(value='yes')

        assert string_obj == local_string_obj, "The objects should be equal"
        assert local_string_obj == string_obj, "The objects should be equal"

    def test_inequality_between_generic_structs(self, int16_struct):
        class LocalInt16Struct(GenericStruct):
            value: INT16

        int16_obj = int16_struct(value=12)
        local_int16_obj = LocalInt16Struct(value=12345)
        assert int16_obj != local_int16_obj, "The objects should not be equal"


class TestNestedObjectCreation:

    def test_nested_object_creation(self):
        class ZeroStruct(GenericStruct):
            fid: UINT64

        class FirstStruct(GenericStruct):
            id: UINT64
            zero_struct: ZeroStruct

        class SecondStruct(GenericStruct):
            sid: UINT64
            first_struct: FirstStruct

        created_object = SecondStruct(sid=123,
                                      first_struct=FirstStruct(id=1234,
                                                               zero_struct=ZeroStruct(fid=555)))
        assert created_object.sid == 123
        assert created_object.first_struct.id == 1234
        assert created_object.first_struct.zero_struct.fid == 555

        packed = created_object.pack()
        unpacked = created_object.unpack(packed)

        assert unpacked.sid == created_object.sid
        assert unpacked.first_struct.id == created_object.first_struct.id
        assert unpacked.first_struct.zero_struct.fid == created_object.first_struct.zero_struct.fid
