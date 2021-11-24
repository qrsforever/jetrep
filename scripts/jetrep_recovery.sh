#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

ARCHIVES_PATH=/var/jetrep/archives

for dir in `ls -r $ARCHIVES_PATH`
do
    echo $dir
done
