#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=srsrtc.service
SRS_DIR=/home/nano/srs
RESTAPI=http://127.0.0.1:8282/apis/systemd/v1/status

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=JetRep SRS Webrtc Service
    Documentation=http://jetrep.hzcsai.com
    After=multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$SRS_DIR
    Restart=always
    RestartSec=10
    ExecStartPre=-/usr/bin/curl -d '{"name": "srsrtc", "status": "starting"}' $RESTAPI
    ExecStart=$SRS_DIR/objs/srs -c $TOP_DIR/etc/srsrtc.conf
    ExecStartPost=/bin/sleep 2
    ExecStartPost=-/usr/bin/curl -d '{"name": "srsrtc", "status": "started"}' $RESTAPI
    ExecStopPost=-/usr/bin/curl -d '{"name": "srsrtc", "status": "stopped"}' $RESTAPI
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
