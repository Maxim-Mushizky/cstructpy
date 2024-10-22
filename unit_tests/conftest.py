import pytest
from src.cstructpy.primitives import (
    BOOL, CHAR, CHAR_ARRAY, PADDING,
    INT8, U_INT8, INT16, U_INT16, INT32, U_INT32, INT64, U_INT64,
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
        value: CHAR_ARRAY(5)

    return StringStruct


@pytest.fixture
def mixed_struct():
    class MixedStruct(GenericStruct):
        bool_val: BOOL
        char_val: CHAR
        int16_val: INT16
        float_val: FLOAT
        string_val: CHAR_ARRAY(10)

    return MixedStruct
