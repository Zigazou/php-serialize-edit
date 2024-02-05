# PHP Serialize Edit

## Description
PHP Serialize Edit is a script which can be included in your projects to
manipulate PHP serialized data from Python 3.

This script only needs Python 3, it uses no common or external library.

It can also be included directly in your Python script.

## Installation
No particular installation, use the script as-is!

## Usage

```PHP
<?php
$data = array(
    "info" => array(
        "surname" => "Frederic",
        "name" => "BISSON",
        "mail" => "zigazou@protonmail.com",
    ),
    "config" => array(
        "format" => "JPEG",
        "quality" => 90,
    ),
);

print(serialize($data) . PHP_EOL);
```

Output of this script:

```
a:2:{s:4:"info";a:3:{s:7:"surname";s:8:"Frederic";s:4:"name";s:6:"BISSON";s:4:"mail";s:22:"zigazou@protonmail.com";}s:6:"config";a:2:{s:6:"format";s:4:"JPEG";s:7:"quality";i:90;}}
```

```python
from php_serialize_edit import php_modify

data = b'a:2:{s:4:"info";a:3:{s:7:"surname";s:8:"Frederic";s:4:"name";s:6:"BISSON";s:4:"mail";s:22:"zigazou@protonmail.com";}s:6:"config";a:2:{s:6:"format";s:4:"JPEG";s:7:"quality";i:90;}}'
print(php_modify(data, b'S:"config"/"quality"=85'))
```

Output of this script:

```
b'a:2:{s:4:"info";a:3:{s:7:"surname";s:8:"Frederic";s:4:"name";s:6:"BISSON";s:4:"mail";s:22:"zigazou@protonmail.com";}s:6:"config";a:2:{s:6:"format";s:4:"JPEG";s:7:"quality";i:85;}}'
```

## Querying expression
To query or modify a PHP serialized structure, this script provides a querying
language.

*Note: This language does not support spaces!*

The querying langage offers 3 modes:

- **get** "G:": retrieve a specific value from a PHP serialized structure.
- **set** "S:": set a specific value in a PHP serialized structure.
- **delete** "D:": delete a specific value in a PHP serialized structure.

To point to a specific value, the querying language has selectors.

A selector is a list of keys separated by a slash "/".

*Note: A selector may be empty which means it targets the root of the serialized PHP structure*

A key is either:

- a **string** surrounded by double quotes and using anti-slash `\` as the
  escape character.
- a **number**, either an integer or a float
- a **boolean**, either `true` or `false` (lowercase)
- a **null**: null

Selector examples:
- `"a"/"b"/3`
- `"a"`
- `3`
- `true/3`

### Get
The "G:" string introducing the get mode is directly followed by a selector.

It returns the pointed value or `None` if it cannot be found.

Get examples:

- `G:` returns the structure as-is
- `G:0` returns the item indexed by the `0` (integer) key in a PHP array
- `G:"a"/"b"` returns the item indexed by `"b"` in a PHP array indexed by `"a"`
  in a PHP array

### Set
The "S:" string introducing the set mode is followed by:

- a **selector**
- an **equal sign** `=`
- a **value**

The value can be:

- a **string** surrounded by double quotes and using anti-slash `\` as the
  escape character.
- a **number**, either an integer or a float
- a **boolean**, either `true` or `false` (lowercase)
- a **null**: null
- an **indexed array** surrounded by square brackets `[` and `]` (key/values
  pair are separated by a comma `,` and key and values are separated by a
  colon `:`)

*Note: if the selector does not point to an existing value, the entire path is created and then the value is set.*

Set examples:

- `S:=3` sets the value to `3` (it will always return `i:3;`)
- `S:0=3` set the value of the first element in a PHP array to `3`
- `S:"a"/"b"="hello"` sets the item indexed by `"b"` in a PHP array indexed by
   `"a"` in a PHP array to the string `"hello"`

## Delete
The "D:" string introducing the delete mode is directly followed by a selector.

It deletes the pointed value if it exists.

Delete examples:

- `D:` returns an empty string
- `D:0` deletes the first element in a PHP array
- `D:"a"/"b"` deletes the `"b"` key in a PHP array indexed by the `"a"` key in
  another PHP array (The `"a"` is not deleted)

## Unserializing
This script uses an intermediate data structure to hold anything necessary to
reencode a PHP structure back to its serialized version.

The intermediate data structure uses standard Python data types:

- PHP integer → Python int
- PHP double → Python float
- PHP array → Python list of tuples (key, value)
- PHP boolean → Python bool
- PHP null → Python None
- PHP object → Python tuple (class_name, list_of_properties) where
  list_of_properties is a list of tuples (key, value)

## License
MIT License
