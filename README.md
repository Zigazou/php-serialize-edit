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

## Delete
The "D:" string introducing the delete mode is directly followed by a selector.

It deletes the pointed value if it exists.

## License
MIT License
