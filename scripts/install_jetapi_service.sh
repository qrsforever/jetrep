#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetapi.service
RESTAPI=http://127.0.0.1:80/apis/svc/status

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

USER=root
ROOT_DIR=/jetrep

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=JetRep Rest API Service
    Documentation=http://jetrep.hzcsai.com
    After=multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$ROOT_DIR
    Environment="PYTHONPATH=$ROOT_DIR"
    Restart=always
    RestartSec=5
    ExecStart=/usr/bin/python3 jetrep/api/server.py --host 0.0.0.0 --port 80 --rpc_host 127.0.0.1 --rpc_port 8181
    TimeoutStartSec=10
    TimeoutStopSec=5
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

$XRUN systemctl stop $SERVICE
$XRUN cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
$XRUN systemctl daemon-reload
if [[ x$1 == x1 ]]
then
    # $XRUN systemctl enable $SERVICE
    $XRUN systemctl start $SERVICE
    $XRUN systemctl status $SERVICE
fi
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
