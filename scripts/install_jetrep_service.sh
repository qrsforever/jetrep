#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetrep.service

USER=root
ROOT_DIR=/jetrep

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=JetRep Main Process
    Documentation=http://jetrep.hzcsai.com
    StartLimitIntervalSec=60
    StartLimitBurst=5
    OnFailure=jetsos.service
    # After=network-online.target
    Wants=network-online.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$ROOT_DIR
    EnvironmentFile=$ROOT_DIR/etc/jetrep.env
    Restart=always
    RestartSec=3
    ExecStartPre=-$ROOT_DIR/scripts/stop_services.sh 1
    ExecStart=/usr/bin/python3 jetrep/core/main.py -c runtime/jetrep.json
    ExecStopPost=-$ROOT_DIR/scripts/stop_services.sh 1
    KillSignal=SIGINT
    TimeoutStartSec=20
    TimeoutStopSec=30
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE
cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
systemctl daemon-reload
systemctl enable $SERVICE
systemctl restart $SERVICE
systemctl status $SERVICE
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
