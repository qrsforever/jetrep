#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd $CUR_DIR/..; pwd)

APP_NAME=`basename $TOP_DIR`

cd $TOP_DIR

DATETIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_VERSION=$(git describe --tags --always)
GIT_COMMIT=$(git rev-parse HEAD | cut -c 1-7)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_NUMBER=$(git rev-list HEAD | wc -l | awk '{print $1}')

VER_MAJOR_NUM=1
VER_MINOR_NUM=0
APP_VERSION=${VER_MAJOR_NUM}.${VER_MINOR_NUM}.${GIT_NUMBER}

echo -n "${APP_VERSION}" > $TOP_DIR/version.txt

cd $TOP_DIR/..

mkdir -p ota

zip -r ota/update_${APP_VERSION}.zip ${APP_NAME} -x@${APP_NAME}/.zipignore
MD5=`md5sum ota/update_${APP_VERSION}.zip | cut -c1-32`

cat > ota/version_info.json <<EOF
{
    "version": "${APP_VERSION}",
    "datetime": "${DATETIME}",
    "compatible": true,
    "force": false,
    "md5": "${MD5}",
    "content": "This is the ota update zip content",
    "git_version": "${GIT_VERSION}",
    "git_commit": "${GIT_COMMIT}",
    "git_branch": "${GIT_BRANCH}"
}
EOF
