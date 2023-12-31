#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetsrs.service
SRS_DIR=/usr/local/srs
RESTAPI=http://127.0.0.1:80/apis/svc/status

USER=root
ROOT_DIR=/jetrep

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
    Restart=on-failure
    RestartSec=10
    ExecStartPre=-/usr/bin/curl -d '{"name": "jetsrs", "status": "starting"}' $RESTAPI
    ExecStart=$SRS_DIR/objs/srs -c $ROOT_DIR/etc/jetsrs.conf
    ExecStartPost=/bin/sleep 2
    ExecStartPost=-/usr/bin/curl -d '{"name": "jetsrs", "status": "started"}' $RESTAPI
    ExecStopPost=-/usr/bin/curl -d '{"name": "jetsrs", "status": "stopped"}' $RESTAPI
    TimeoutStartSec=10
    TimeoutStopSec=5
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE
cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
systemctl daemon-reload
if [[ x$1 == x1 ]]
then
    # systemctl enable $SERVICE
    systemctl restart $SERVICE
    systemctl status $SERVICE
fi
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
