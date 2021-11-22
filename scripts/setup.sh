#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

_apt_install() {
    $XRUN apt install -y $*    
}

_pip_install() {
    $XRUN pip3 install $*    
}

## Environment Prepare

_pip_install pyudev flask flask_cors zerorpc


## Scripts
$XRUN chmod +x -R $CUR_DIR/*.sh
$XRUN chmod +x -R $TOP_DIR/etc/crontab/*
$XRUN chmod +x -R $TOP_DIR/etc/shell/*


## Install Systemd and Services

. $CUR_DIR/stop_services.sh
. $CUR_DIR/install_crontab.sh
. $CUR_DIR/install_jetapi_service.sh
. $CUR_DIR/install_jetgst_service.sh
. $CUR_DIR/install_jetsrs_service.sh
. $CUR_DIR/install_jetrep_service.sh
