import pytest
from src.cstructpy.primitives import (
    BOOL, CHAR, CharArray, PADDING,
    INT8, UINT8, INT16, UINT16, INT32, UINT32, INT64, UINT64,
    FLOAT, DOUBLE
)
from src.cstructpy import GenericStruct


# Fixtures for commonly used struct types
@pytest.fixture
def bool_struct():
    class BoolStruct(GenericStruct):
        value: BOOL

    return BoolStruct


@pytest.fixture
def char_struct():
    class CharStruct(GenericStruct):
        value: CHAR

    return CharStruct


@pytest.fixture
def string_struct():
    class StringStruct(GenericStruct):
        value: CharArray(5)

    return StringStruct


@pytest.fixture
def int16_struct():
    class Int16Struct(GenericStruct):
        value: INT16

    return Int16Struct


@pytest.fixture
def mixed_struct():
    class MixedStruct(GenericStruct):
        bool_val: BOOL
        char_val: CHAR
        int16_val: INT16
        float_val: FLOAT
        string_val: CharArray(10)

    return MixedStruct


@pytest.fixture
def complex_struct():
    class MixedStruct(GenericStruct):
        bool_val: BOOL
        char_val: CHAR
        int16_val: INT16
        float_val: FLOAT
        uint16_val: UINT16
        uint32_val: UINT32
        uint64_val: UINT64

    return MixedStruct


@pytest.fixture
def arrays_struct_6():
    class ArraysStruct6(GenericStruct):
        bool_array_6: BOOL[6]
        int16_array_6: INT16[6]
        float_array_6: FLOAT[6]
        uint16_array_6: UINT16[6]
        uint32_array_6: UINT32[6]
        uint64_array_6: UINT64[6]
    return ArraysStruct6
