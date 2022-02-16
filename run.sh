#! /bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # cygwin compatibility, this comment is required, don't put anything except comments (even empty lines) before this line

cdir=$(dirname $0)

export PYTHONPATH=${PYTHONPATH}:${cdir}

pip3 install -r ${cdir}/tools/requirements.txt --user
# pip3 freeze > ${cdir}/tools/requirements.txt
python3 $@
