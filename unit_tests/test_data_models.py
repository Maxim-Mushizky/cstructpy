import pytest
from src.cstructpy.primitives import (
    BOOL, CHAR, CharArray, PADDING,
    INT8, UINT8, INT16, UINT16, INT32, UINT32, INT64, UINT64,
    FLOAT, DOUBLE
)
from src.cstructpy import GenericStruct


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
        with pytest.raises(ValueError):
            s.value = "True"
        with pytest.raises(ValueError):
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

        with pytest.raises(ValueError):
            FloatStruct(value="3.14")

        s = FloatStruct(value=1.0)
        with pytest.raises(ValueError):
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
