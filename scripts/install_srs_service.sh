#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=srs.service
SRS_DIR=/home/nano/srs

if [[ 0 != $(id -u) ]]
then
    echo "Use root execute!!!"
    exit 0
fi

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=Gst pipeline start launch
    Documentation=http://jetrep.hzcsai.com
    After=multi-user.target

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$SRS_DIR
    Restart=always
    RestartSec=5
    ExecStart=$SRS_DIR/objs/srs -c $TOP_DIR/etc/srs.conf
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
