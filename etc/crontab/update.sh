#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

zip_path=$1
dst_path=$2

if [[ -f $zip_path ]]
then
    filename=`basename $zip_path`
    if [[ ${filename##*.} == "zip" ]]
    then
        cal_md5=`md5sum $zip_path | cut -d\  -f1`
        if [[ x$3 == x ]]
        then
            zip_md5=`echo ${filename%%.*} | cut -d_ -f2`
            if [[ ${#zip_md5} != 32 ]]
            then
                zip_md5=$cal_md5
            fi
        else
            zip_md5=$3
        fi
        if [[ $zip_md5 == $cal_md5 ]]
        then
            unzip -qo $zip_path -d $dst_path/$zip_md5
            # rm -f /jetrep > /dev/null
            # ln -s $dst_path/$zip_md5 /jetrep
            exit 0
        fi
    fi
fi
exit -1
