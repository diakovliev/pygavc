#!/bin/bash

SCRIPT_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
PARENT_DIR="$(dirname $SCRIPT_DIR)"

export PYTHONPATH="$PYTHONPATH:$SCRIPT_DIR:$PARENT_DIR"
python -m utils_test -v
python -m version_test -v
python -m versions_matcher_test -v
python -m versions_comparator_test -v
python -m sparts_table_comparator_test -v
python -m versions_filter_test -v
