#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=repapi.service
RESTAPI=http://127.0.0.1:8282/apis/systemd/v1/status

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

USER=root

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
    WorkingDirectory=$TOP_DIR
    Environment="PYTHONPATH=$TOP_DIR"
    Restart=always
    RestartSec=5
    ExecStart=/usr/bin/python3 jetrep/api/server.py --host 127.0.0.1 --port 8282 --rpc_host 127.0.0.1 --rpc_port 8181
    TimeoutStartSec=10
    TimeoutStopSec=5
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

$XRUN cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
$XRUN systemctl daemon-reload
# $XRUN systemctl enable $SERVICE
$XRUN systemctl restart $SERVICE
$XRUN systemctl status $SERVICE
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
