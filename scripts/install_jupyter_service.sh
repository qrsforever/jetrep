#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jupyter.service
HOST_IP=172.16.0.35
WORKSPACE=/home/nano/omega

XRUN=

if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

jupyter notebook --no-browser --notebook-dir=$WORKSPACE --allow-root --ip=0.0.0.0 --port=8118

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=Notebook Service
    Documentation=http://jetrep.hzcsai.com
    After=network.target multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$WORKSPACE
    Restart=always
    RestartSec=5
    ExecStartPre=/sbin/mount.nfs $HOST_IP:/blog/public $WORKSPACE
    ExecStart=/usr/bin/jupyter notebook --no-browser --notebook-dir=$WORKSPACE --allow-root --ip=0.0.0.0 --port=8118
    TimeoutStartSec=10
    TimeoutStopSec=5
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

$XRUN cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
$XRUN systemctl daemon-reload
$XRUN systemctl enable $SERVICE
$XRUN systemctl restart $SERVICE
$XRUN systemctl status $SERVICE
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f"
echo ""
echo "-------------------------------"
