#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetrep.service

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

USER=root

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=JetRep Main Process
    Documentation=http://jetrep.hzcsai.com
    After=multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$TOP_DIR
    EnvironmentFile=$TOP_DIR/etc/jetrep.env
    Restart=always
    RestartSec=3
    ExecStartPre=-/bin/bash $TOP_DIR/scripts/stop_services.sh 1
    ExecStart=/usr/bin/python3 jetrep/core/main.py -c runtime/jetrep.json
    ExecStopPost=-/bin/bash $TOP_DIR/scripts/stop_services.sh 1
    KillSignal=SIGINT
    TimeoutStartSec=20
    TimeoutStopSec=30
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
    $XRUN systemctl enable $SERVICE
    $XRUN systemctl restart $SERVICE
    $XRUN systemctl status $SERVICE
fi
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
