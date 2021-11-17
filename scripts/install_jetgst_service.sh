#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetgst.service
RESTAPI=http://127.0.0.1:8282/apis/svc/v1/status

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

USER=root

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=Gst pipeline start launch
    Documentation=http://jetrep.hzcsai.com
    After=srsrtc.service multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$TOP_DIR
    EnvironmentFile=$TOP_DIR/etc/jetgst.env
    Restart=always
    RestartSec=10
    # ExecStartPre=-/bin/systemctl restart nvargus-daemon
    ExecStartPre=-/usr/bin/curl -d '{"name": "jetgst", "status": "starting"}' $RESTAPI
    ExecStart=/usr/bin/python3 jetrep/stream -c etc/jetgst.json
    ExecStartPost=/bin/sleep 2
    ExecStartPost=-/usr/bin/curl -d '{"name": "jetgst", "status": "started"}' $RESTAPI
    ExecStopPost=-/usr/bin/curl -d '{"name": "jetgst", "status": "stopped"}' $RESTAPI
    TimeoutStartSec=10
    TimeoutStopSec=5
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

$XRUN cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
$XRUN systemctl daemon-reload
if [[ x$1 == x1 ]]
then
    # $XRUN systemctl enable $SERVICE
    $XRUN systemctl restart $SERVICE
    $XRUN systemctl status $SERVICE
fi
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
