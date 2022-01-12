#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)

if [[ 0 != $(id -u) ]]
then
    echo "Not root perm"
    exit -1
fi

_apt_install() {
    apt install -y $*    
}

_pip_install() {
    pip3 install $*    
}

## Environment Prepare

# _pip_install flask flask_cors zerorpc

if [[ ! -L /usr/local/cuda ]]
then
    ln -s /usr/local/cuda-10.2 /usr/local/cuda
fi


## Scripts
chmod +x -R $CUR_DIR/*.sh
chmod +x -R $TOP_DIR/etc/crontab/*
chmod +x -R $TOP_DIR/etc/shell/*


## Install Systemd and Services

. $CUR_DIR/stop_services.sh
. $CUR_DIR/install_crontab.sh
. $CUR_DIR/install_jetsos_service.sh
. $CUR_DIR/install_jetapi_service.sh
. $CUR_DIR/install_jetgst_service.sh
. $CUR_DIR/install_jetsrs_service.sh
. $CUR_DIR/install_jetrep_service.sh
