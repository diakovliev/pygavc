#!/bin/bash

SCRIPT_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
PARENT_DIR="$(dirname $SCRIPT_DIR)"

export PYTHONPATH="$PYTHONPATH:$SCRIPT_DIR:$PARENT_DIR"
python -m utils_test -v
