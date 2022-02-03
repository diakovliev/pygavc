#! /bin/sh

pip install -r requirements.txt
# pip freeze > requirements.txt

TESTS=$(cat<<EOF
test.build_config
test.install_specs
test.utils_test
test.version_test
test.versions_matcher_test
test.versions_comparator_test
test.sparts_table_comparator_test
test.versions_filter_test
EOF
)

set -e

for t in ${TESTS}; do
	python -m ${t} -v
done
