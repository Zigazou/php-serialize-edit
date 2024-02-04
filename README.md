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

## License
MIT License
