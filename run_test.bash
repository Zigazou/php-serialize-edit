#!/usr/bin/env bash
export PYTHONPATH="$(pwd)/src":$PYTHONPATH
python3 tests/php_serialize_edit.test.py
