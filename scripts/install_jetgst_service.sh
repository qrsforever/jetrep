#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetgst.service
RESTAPI=http://0.0.0.0:8282/apis/systemd/v1/status

if [[ 0 != $(id -u) ]]
then
    echo "Use root execute!!!"
    exit 0
fi

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=Gst pipeline start launch
    Documentation=http://jetrep.hzcsai.com
    After=srs.service multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$TOP_DIR
    EnvironmentFile=$TOP_DIR/etc/jetgst.env
    Restart=always
    RestartSec=5
    ExecStartPre=-/bin/systemctl restart nvargus-daemon
    ExecStart=/usr/bin/python3 jetrep/stream -c etc/jetgst.json
    ExecStartPost=/usr/bin/curl -d '{"name": "jetgst", "status": "started"}' $RESTAPI
    ExecStopPost=/usr/bin/curl -d '{"name": "jetgst", "status": "stopped"}' $RESTAPI
    TimeoutStartSec=10
    TimeoutStopSec=5
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
systemctl daemon-reload
systemctl enable $SERVICE
systemctl restart $SERVICE
systemctl status $SERVICE
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f"
echo ""
echo "-------------------------------"
