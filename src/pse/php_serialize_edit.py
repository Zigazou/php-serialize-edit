# /usr/bin/env python3
"""
This module provides classes for parsing and unserializing PHP serialized data.

The module includes the following classes: - ParseError: Exception raised when
an error occurs during parsing.

- SerializeError: Exception raised when an error occurs during unserialization
  of PHP serialized value.

- Parser: A class that represents a parser for PHP serialized data.

- PHPUnserializer: A class that extends the Parser class and provides methods to
  decode PHP serialized values.

- PHPSerializer: A class that provides methods to encode Python values into PHP
  serialized format.

- Query: A class that extends the Parser class and provides methods to parse a
  query string.

The module also includes several constants representing PHP serialized data
types and separators.

Usage:

"""

# Constants for serialize/unserialize PHP functions
# https://www.php.net/manual/fr/function.serialize.php
PHP_STRING = b"s"
PHP_INT = b"i"
PHP_BOOL = b"b"
PHP_NULL = b"N"
PHP_ARRAY = b"a"
PHP_OBJECT = b"O"
PHP_DECIMAL = b"d"
PHP_FIELD_SEPARATOR = b":"
PHP_END_VALUE = b";"
PHP_START_ARRAY = b"{"
PHP_END_ARRAY = b"}"
PHP_STRING_DELIMITER = b'"'

# Generic parsing constants
MINUS = b"-"
DIGIT_NINE = b"9"
DIGIT_ZERO = b"0"
DECIMAL_DOT = b"."
EMPTY = b""

# Constants for query parsing
QUERY_START_STRING = b'"'
QUERY_END_STRING = b'"'
QUERY_ESCAPE = b"\\"
QUERY_EQUAL = b"="
QUERY_PATH_SEPARATOR = b"/"
QUERY_GET = b"G"
QUERY_SET = b"S"
QUERY_DELETE = b"D"
QUERY_COMMAND_SEPARATOR = b":"
QUERY_START_ARRAY = b"["
QUERY_END_ARRAY = b"]"
QUERY_START_OBJECT = b"{"
QUERY_END_OBJECT = b"}"
QUERY_KEY_VALUE_SEPARATOR = b":"
QUERY_ITEM_SEPARATOR = b","
QUERY_TRUE = b"true"
QUERY_FALSE = b"false"
QUERY_NULL = b"null"


def is_valid_int_start(data: bytes) -> bool:
    """Check if the given byte is a valid start for an integer value."""
    return DIGIT_ZERO <= data <= DIGIT_NINE or data == MINUS

def is_object(data) -> bool:
    """Check if the given data is a PHP object."""
    return (
        isinstance(data, tuple)
        and len(data) == 2
        and isinstance(data[0], bytes)
        and isinstance(data[1], list)
    )

class ParseError(Exception):
    """Raised when an error occurs during parsing"""

    def __init__(self, position: int, message: str):
        self.position = position
        self.message = message
        super().__init__(
            f"Parse error at byte {self.position}: {self.message}"
        )


class SerializeError(Exception):
    """Raised when an error occurs during unserialization of PHP serialized
    value"""


class Parser:
    """
    A class that represents a parser for PHP serialized data.

    The Parser class is meant to be derived from to provide specific parsing.

    Attributes:
        data (bytes): The stream of serialized data.

        current (int): The current position in the data stream.

    Methods:
        __init__(self, data: bytes): Initializes the `Parser` object with the
        given data.

        reset(self, data: bytes): Resets the parser with new data.

        end_of_data(self) -> bool: Checks if the parser has reached the end of
        the data stream.

        next_byte(self, increment: int = 1): Moves the current position in the
        data stream forward by the specified increment.

        chunk(self, length: int = 1) -> bytes: Returns a chunk of bytes from the
        data stream.

        read_until(self, stop: bytes) -> bytes: Reads bytes from the data stream
        until the specified stop sequence is encountered.

        read_bytes(self, length: int = 1) -> bytes: Reads the specified number
        of bytes from the data stream.

        read_must(self, expected: bytes) -> bytes: Reads and consumes specific
        bytes from the data stream, raising an exception if the expected bytes
        are not found.
    """

    def __init__(self, data: bytes):
        self.reset(data)

    def reset(self, data: bytes):
        """Reset the parser with new data"""
        # Stream to unserialize.
        self.data = data

        # Current position in the stream.
        self.current = 0

    def end_of_data(self) -> bool:
        """Checks if the parser has reached the end of the data stream"""
        return self.current >= len(self.data)

    def next_byte(self, increment: int = 1):
        """Moves the current position in the data stream forward by the
        specified increment (defaults to 1)"""
        self.current += increment

    def chunk(self, length: int = 1):
        """Returns a chunk of bytes from the data stream without moving the
        current position forward. Without parameters, returns the next byte."""
        return self.data[self.current:self.current+length]

    def read_until(self, stop: bytes):
        """Reads bytes from the data stream until the specified stop sequence"""
        before, _ = self.data[self.current:].split(stop, 1)
        self.next_byte(len(before))
        return before

    def read_bytes(self, length: bytes = 1):
        """Reads the specified number of bytes from the data stream."""
        start = self.chunk(length)
        self.next_byte(len(start))
        return start

    def read_must(self, expected: bytes) -> bytes:
        """Consumes specific bytes, raises an exception otherwise"""
        if len(expected) > (len(self.data) - self.current):
            raise ParseError(
                self.current,
                f"Not enough bytes while expecting {expected}."
            )

        chunk = self.chunk(len(expected))
        if chunk != expected:
            raise ParseError(
                self.current,
                f"Expected {expected} but {chunk} appeared."
            )

        self.next_byte(len(expected))


class PHPUnserializer(Parser):
    """A class for deserializing PHP serialized data"""

    def __init__(self, data: bytes):
        self.callbacks = {
            PHP_STRING: self._string_from_bytes,
            PHP_INT: self._int_from_bytes,
            PHP_BOOL: self._bool_from_bytes,
            PHP_NULL: self._null_from_bytes,
            PHP_ARRAY: self._array_from_bytes,
            PHP_DECIMAL: self._decimal_from_bytes,
            PHP_OBJECT: self._object_from_bytes,
        }

        super().__init__(data)

    def _string_from_bytes(self) -> bytes:
        """Decode a PHP_ string"""
        self.read_must(PHP_STRING)
        self.read_must(PHP_FIELD_SEPARATOR)
        size = int(self.read_until(PHP_FIELD_SEPARATOR))
        self.read_must(PHP_FIELD_SEPARATOR)
        self.read_must(PHP_STRING_DELIMITER)
        value = self.read_bytes(size)
        self.read_must(PHP_STRING_DELIMITER)
        self.read_must(PHP_END_VALUE)

        return value

    def _int_from_bytes(self) -> int:
        """Decode a PHP_ integer"""
        self.read_must(PHP_INT)
        self.read_must(PHP_FIELD_SEPARATOR)
        value = int(self.read_until(PHP_END_VALUE))
        self.read_must(PHP_END_VALUE)

        return value

    def _decimal_from_bytes(self) -> float:
        """Decode a PHP_ decimal"""
        self.read_must(PHP_DECIMAL)
        self.read_must(PHP_FIELD_SEPARATOR)
        value = float(self.read_until(PHP_END_VALUE))
        self.read_must(PHP_END_VALUE)

        return value

    def _bool_from_bytes(self) -> bool:
        """Decode a PHP_ boolean"""
        self.read_must(PHP_BOOL)
        self.read_must(PHP_FIELD_SEPARATOR)
        value = bool(int(self.read_until(PHP_END_VALUE)))
        self.read_must(PHP_END_VALUE)

        return value

    def _null_from_bytes(self) -> None:
        """Decode a PHP_ null value"""
        self.read_must(PHP_NULL)
        self.read_must(PHP_END_VALUE)

    def _array_from_bytes(self) -> list:
        """Decode a PHP_ array"""
        self.read_must(PHP_ARRAY)
        self.read_must(PHP_FIELD_SEPARATOR)
        size = int(self.read_until(PHP_FIELD_SEPARATOR))
        self.read_must(PHP_FIELD_SEPARATOR)
        self.read_must(PHP_START_ARRAY)

        array = [(self.from_bytes(), self.from_bytes()) for _ in range(size)]

        self.read_must(PHP_END_ARRAY)

        return array

    def _object_from_bytes(self) -> tuple[bytes, list]:
        """Decode a PHP object"""
        self.read_must(PHP_OBJECT)
        self.read_must(PHP_FIELD_SEPARATOR)

        size = int(self.read_until(PHP_FIELD_SEPARATOR))
        self.read_must(PHP_FIELD_SEPARATOR)
        self.read_must(PHP_STRING_DELIMITER)
        class_name = self.read_bytes(size)
        self.read_must(PHP_STRING_DELIMITER)
        self.read_must(PHP_FIELD_SEPARATOR)

        count = int(self.read_until(PHP_FIELD_SEPARATOR))
        self.read_must(PHP_FIELD_SEPARATOR)
        self.read_must(PHP_START_ARRAY)

        props = [(self.from_bytes(), self.from_bytes()) for _ in range(count)]

        self.read_must(PHP_END_ARRAY)

        return (class_name, props)

    def from_bytes(self):
        """Decode a PHP_ serialized value from a bytes object"""
        php_type = self.chunk()
        if php_type not in self.callbacks:
            raise ParseError(
                self.current,
                f"Unknown PHP_ object type '{php_type}'"
            )

        return self.callbacks[php_type]()


class PHPSerializer:
    """
    A class for serializing Python objects into PHP serialized format.

    This class provides methods to convert various Python data types into their
    corresponding PHP serialized format. It supports strings, booleans,
    integers, floats, and arrays.

    Usage:
        serializer = PHPSerializer()

        serialized_data = serializer.to_bytes(data)

    Note:
        - The serialized data is returned as bytes.

        - If the input data type is not supported, a SerializeError is raised.
    """

    def __init__(self, data):
        self.reset(data)

    def reset(self, data):
        """Reset the serializer with new data"""
        self.data = data

    def _string_to_bytes(self) -> bytes:
        return (
            PHP_STRING
            + PHP_FIELD_SEPARATOR
            + bytes(str(len(self.data)), "utf-8")
            + PHP_FIELD_SEPARATOR
            + PHP_STRING_DELIMITER
            + self.data
            + PHP_STRING_DELIMITER
            + PHP_END_VALUE
        )

    def _bool_to_bytes(self) -> bytes:
        return (
            PHP_BOOL + PHP_FIELD_SEPARATOR +
            bytes(str(int(self.data)), "utf-8") + PHP_END_VALUE
        )

    def _int_to_bytes(self) -> bytes:
        return (
            PHP_INT + PHP_FIELD_SEPARATOR +
            bytes(str(self.data), "utf-8") + PHP_END_VALUE
        )

    def _float_to_bytes(self) -> bytes:
        return (
            PHP_DECIMAL + PHP_FIELD_SEPARATOR +
            bytes(str(self.data), "utf-8") + PHP_END_VALUE
        )

    def _array_to_bytes(self) -> bytes:
        return (
            PHP_ARRAY
            + PHP_FIELD_SEPARATOR
            + bytes(str(len(self.data)), "utf-8")
            + PHP_FIELD_SEPARATOR
            + PHP_START_ARRAY
            + EMPTY.join([
                PHPSerializer(key).to_bytes() +
                PHPSerializer(value).to_bytes() for (key, value) in self.data
            ])
            + PHP_END_ARRAY
        )

    def _object_to_bytes(self) -> bytes:
        class_name, properties = self.data
        return (
            PHP_OBJECT
            + PHP_FIELD_SEPARATOR
            + bytes(str(len(class_name)), "utf-8")
            + PHP_FIELD_SEPARATOR
            + PHP_STRING_DELIMITER
            + class_name
            + PHP_STRING_DELIMITER
            + PHP_FIELD_SEPARATOR
            + bytes(str(len(properties)), "utf-8")
            + PHP_FIELD_SEPARATOR
            + PHP_START_ARRAY
            + EMPTY.join([
                PHPSerializer(property_name).to_bytes() +
                PHPSerializer(property_value).to_bytes()
                for (property_name, property_value) in properties
            ])
            + PHP_END_ARRAY
        )

    def to_bytes(self) -> bytes:
        """Converts the given Python object into PHP serialized format."""
        if isinstance(self.data, bytes):
            return self._string_to_bytes()

        if isinstance(self.data, bool):
            return self._bool_to_bytes()

        if isinstance(self.data, int):
            return self._int_to_bytes()

        if isinstance(self.data, float):
            return self._float_to_bytes()

        if isinstance(self.data, list):
            return self._array_to_bytes()

        if is_object(self.data):
            return self._object_to_bytes()

        raise SerializeError(f"Cannot encode {self.data}")


class Query(Parser):
    """A Query is a class that extends the Parser class and provides methods to
    parse a query string and execute an expression."""

    def __init__(self, structure):
        super().__init__(EMPTY)
        self.structure = structure

        self.callbacks = {
            QUERY_START_STRING: self._parse_string,
            QUERY_START_ARRAY: self._parse_array,
            QUERY_START_OBJECT: self._parse_object,
            QUERY_TRUE[0:1]: self._parse_true,
            QUERY_FALSE[0:1]: self._parse_false,
            QUERY_NULL[0:1]: self._parse_null,
        }


    def _parse_string(self) -> bytes:
        self.read_must(QUERY_START_STRING)

        escaping = False
        string = EMPTY
        while not self.end_of_data():
            if escaping:
                escaping = False
                string += self.read_bytes()
            elif self.chunk() == QUERY_ESCAPE:
                escaping = True
                self.next_byte()
            elif self.chunk() == QUERY_END_STRING:
                self.read_must(QUERY_END_STRING)
                return string
            else:
                string += self.read_bytes()

        if escaping:
            raise ParseError(self.current, "Incomplete escape sequence")

        raise ParseError(self.current, "Unterminated string")


    def _parse_number(self):
        number_string = EMPTY
        if self.chunk() == MINUS:
            number_string = MINUS
            self.next_byte()

        while not self.end_of_data():
            if not DIGIT_ZERO <= self.chunk() <= DIGIT_NINE:
                break

            number_string += self.chunk()
            self.next_byte()

        if number_string == EMPTY:
            raise ParseError(self.current, "Expected a digit")

        if self.chunk() != DECIMAL_DOT:
            return int(number_string)

        self.next_byte()
        number_string += DECIMAL_DOT
        while not self.end_of_data():
            if not DIGIT_ZERO <= self.chunk() <= DIGIT_NINE:
                break

            number_string += self.chunk()
            self.next_byte()

        return float(number_string)

    def _parse_selector(self) -> list:
        require_selector = True

        selector = []

        if self.end_of_data() or self.chunk() == QUERY_EQUAL:
            return selector

        while require_selector:
            current_byte = self.chunk()
            if current_byte == QUERY_START_STRING:
                item = self._parse_string()
                require_selector = False
            elif is_valid_int_start(current_byte):
                item = self._parse_number()
                require_selector = False
            else:
                raise ParseError(self.current, "Expected string or number")

            selector.append(item)

            if not self.end_of_data():
                next_byte = self.chunk()
                if next_byte == QUERY_PATH_SEPARATOR:
                    require_selector = True
                    self.read_must(QUERY_PATH_SEPARATOR)
                    continue

                if next_byte == QUERY_EQUAL:
                    require_selector = False
                    continue

                raise ParseError(self.current, "Unexpected char in selector")

        return selector

    def _parse_array(self) -> list:
        self.read_must(QUERY_START_ARRAY)

        array = []
        while not self.end_of_data() and self.chunk() != QUERY_END_ARRAY:
            key = self._parse_value()
            self.read_must(QUERY_KEY_VALUE_SEPARATOR)
            value = self._parse_value()
            array.append((key, value))

            if self.chunk() == QUERY_ITEM_SEPARATOR:
                self.read_must(QUERY_ITEM_SEPARATOR)
                continue

            if self.chunk() != QUERY_END_ARRAY:
                raise ParseError(self.current, "Unexpected char in array")

        self.read_must(QUERY_END_ARRAY)

        return array

    def _parse_object(self) -> tuple[bytes, list]:
        self.read_must(QUERY_START_OBJECT)

        class_name = self._parse_string()
        if len(class_name) == 0:
            raise ParseError(self.current, "Class name can not be empty")

        self.read_must(QUERY_ITEM_SEPARATOR)
        properties = self._parse_array()

        self.read_must(QUERY_END_OBJECT)

        return (class_name, properties)

    def _parse_true(self):
        self.read_must(QUERY_TRUE)
        return True

    def _parse_false(self):
        self.read_must(QUERY_FALSE)
        return False

    def _parse_null(self):
        self.read_must(QUERY_NULL)

    def _parse_value(self):
        """Parse a value from the query string"""
        chunk = self.chunk()
        if chunk in self.callbacks:
            return self.callbacks[chunk]()

        if is_valid_int_start(chunk):
            return self._parse_number()

        raise ParseError(self.current, "Expected a value")

    def _parse_command(self):
        """Parse a command from the query string"""
        command_id = self.chunk()

        if command_id not in [QUERY_GET, QUERY_SET, QUERY_DELETE]:
            raise ParseError(self.current, f"Unknown command '{command_id}'.")

        self.read_must(command_id)
        self.read_must(QUERY_COMMAND_SEPARATOR)
        selector = self._parse_selector()

        if command_id == QUERY_SET:
            self.read_must(QUERY_EQUAL)
            value = self._parse_value()
        else:
            value = None

        return (command_id, selector, value)


    def _set(self, selector, value, structure):
        """Set a value in the structure"""
        if selector == []:
            return value

        if isinstance(structure, list):
            key = selector[0]
            modified_data = []
            value_must_be_created = True
            for item_key, item_value in structure:
                if key == item_key:
                    item_value = self._set(selector[1:], value, item_value)
                    value_must_be_created = False

                modified_data.append((item_key, item_value))

            if value_must_be_created:
                modified_data.append((key, self._set(selector[1:], value, [])))

            return modified_data

        if is_object(structure):
            return (structure[0], self._set(selector, value, structure[1]))

        raise ValueError("Expected list of object")

    def _get(self, selector, structure):
        """Get a value from the structure"""
        if selector == []:
            return structure

        if isinstance(structure, list):
            to_get = selector[0]

            for key, value in structure:
                if key == to_get:
                    return self._get(selector[1:], value)

        if is_object(structure):
            return self._get(selector, structure[1])

        return None

    def _delete(self, selector, structure):
        """Delete a value from the structure"""
        if selector == []:
            return structure

        if isinstance(structure, list):
            to_delete = selector[0]
            if len(selector) == 1:
                return [
                    (key, value) for key, value in structure if key != to_delete
                ]

            modified = []
            for key, value in structure:
                if key == to_delete:
                    modified.append((key, self._delete(selector[1:], value)))
                else:
                    modified.append((key, value))

            return modified

        if is_object(structure):
            return (structure[0], self._delete(selector, structure[1]))

        raise ValueError("Expected a list or an object")

    def run(self, expression: bytes):
        """Run the query on the structure"""
        self.reset(expression)
        (command, selector, value) = self._parse_command()

        if command == QUERY_SET:
            self.structure = self._set(selector, value, self.structure)
            return self.structure

        if command == QUERY_GET:
            return self._get(selector, self.structure)

        if command == QUERY_DELETE:
            return self._delete(selector, self.structure)

        return None


def php_serialize(value) -> bytes:
    """
    Serializes a Python object into a PHP serialized string.

    Args:
        value: The Python object to be serialized.

    Returns:
        bytes: The PHP serialized string.

    """
    return PHPSerializer(value).to_bytes()


def php_unserialize(data: bytes):
    """
    Unserializes PHP data from bytes.

    Args:
        data (bytes): The serialized PHP data.

    Returns:
        The unserialized Python object.
    """
    return PHPUnserializer(data).from_bytes()


def php_modify(data: bytes, expression: bytes):
    """
    Modifies the given PHP serialized data using the provided expression.

    Args:
        data (bytes): The PHP serialized data to be modified.
        expression (bytes): The expression to apply to the serialized data.

    Returns:
        bytes: The modified PHP serialized data.
    """
    unserialized = php_unserialize(data)
    modified = Query(unserialized).run(expression)
    return php_serialize(modified)
