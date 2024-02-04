#!/usr/bin/env bash
export PYTHONPATH="$(pwd)/src":$PYTHONPATH
python3 test/php_serialize_edit.test.py