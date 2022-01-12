#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

VALID_VERSION="default"

for dir in `ls -r ${ARCHIVES_PATH:-/var/jetrep/archives}`
do
    if [[ "$dir" != "$VALID_VERSION" ]]
    then
        echo $ARCHIVES_PATH/$dir/$CONFIG_VALID_NOD
        if [[ -f $ARCHIVES_PATH/$dir/$CONFIG_VALID_NOD ]]
        then
            VALID_VERSION=$dir
            break
        else
            rm -rf $ARCHIVES_PATH/$dir
        fi
    fi
done

rm /jetrep
ln -s $ARCHIVES_PATH/$VALID_VERSION/jetrep /jetrep
systemctl reset-failed jetrep
systemctl restart jetrep
exit 0
