# cstructpy v0.1.0

[![Build Status](https://github.com/Maxim-Mushizky/cstructpy/actions/workflows/ci.yml/badge.svg)](https://github.com/Maxim-Mushizky/cstructpy/actions)
[![PyPI version](https://badge.fury.io/py/cstructpy.svg)](https://badge.fury.io/py/cstructpy)
[![Python versions](https://img.shields.io/pypi/pyversions/cstructpy)](https://pypi.org/project/cstructpy/)

**cstructpy** is a Python package designed for binary serialization and deserialization of structured data using custom
primitive types. It provides a simple interface for packing and unpacking binary data based on field definitions using
Python's `struct` module.
The motivation for this package is to have a data validation using type annotations, similar to pydantic but for binary
data. Therefore this package is best when used alongside pydantic.BaseModel or dataclasses.dataclass since it allows a
similar class structure and object creation

## Features

- Custom primitive types for integers, floating points, characters, and arrays.
- Dynamically create structured classes with flexible field definitions.
- Serialize/deserialize data to/from binary formats easily.
- Supports both signed and unsigned integer types (e.g., `INT8`, `U_INT8`, `INT16`, etc.).
- Support for alignment padding and fixed-length character arrays.

## Installation

Install the package via pip:

```bash
pip install cstructpy
```

## Usage

Here's a quick guide to using cstructpy to create your own structured binary data:

### Defining a Structured Class

You can define a new class that extends GenericStruct and define the fields using the custom primitive types from
primitives.py.

```python
from cstructpy import GenericStruct
from cstructpy.primitives import INT8, U_INT16, FLOAT


class MyDataStructure(GenericStruct):
    field1: INT8
    field2: U_INT16
    field3: FLOAT


# Create an instance with field values
data_instance = MyDataStructure(field1=-128, field2=65535, field3=3.14)

# Pack the instance into binary format
binary_data = data_instance.pack()
print(binary_data)  # Output: b'\x80\xff\xff\xc3\xf5H@'

# Unpack the binary data back into a structured instance
new_instance = MyDataStructure.unpack(binary_data)
print(new_instance.to_dict())  # Output: {'field1': -128, 'field2': 65535, 'field3': 3.14}


```

## Primitive Types

The package provides the following primitive types for defining fields:

* **INT8**: 8-bit signed integer.
* **U_INT8**: 8-bit unsigned integer.
* **INT16**: 16-bit signed integer.
* **U_INT16**: 16-bit unsigned integer.
* **INT32**: 32-bit signed integer.
* **U_INT32**: 32-bit unsigned integer.
* **INT64**: 64-bit signed integer.
* **U_INT64**: 64-bit unsigned integer.
* **FLOAT**: 32-bit floating point number.
* **DOUBLE**: 64-bit floating point number.
* **CHAR**: Single character.
* **CHAR_ARRAY**: Fixed-length character array.
* **BOOL**: Boolean value.
* **PADDING**: Padding type used for alignment.

## Example: Packing and Unpacking

```python
from cstructpy import GenericStruct
from cstructpy.primitives import INT16, CHAR_ARRAY


class AnotherStruct(GenericStruct):
    number: INT16
    message: CHAR_ARRAY(10)


# Create an instance
example = AnotherStruct(number=42, message="hello")

# Pack it to binary
binary_data = example.pack()

# Unpack binary data back into an instance
unpacked_example = AnotherStruct.unpack(binary_data)

# Convert to dictionary
print(unpacked_example.to_dict())  # Output: {'number': 42, 'message': 'hello'}


```

## Validation

Each field type has its own validation rules. For example, INT8 will only accept values between -128 and 127. If you try
to set a value outside this range, a ValueError will be raised.

```python

from cstructpy.primitives import INT8

int_field = INT8()
int_field.validate(-128)  # Valid
int_field.validate(128)  # Raises ValueError: Value 128 is greater than maximum 127

```

## Running Tests

The package includes unit tests, which you can run using pytest:

```bash
pytest unit_tests
```

## GitHub Actions

This repository uses GitHub Actions to automatically run linting, type checking, and tests. The pipeline includes:

* flake8 for linting.
* mypy for type checking.
* pytest for running tests.

## Contributing

Feel free to open issues and submit pull requests. Make sure to run all tests before submitting your changes.

## License

This project is licensed under the MIT License.
