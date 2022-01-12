#!/bin/bash

USER=$(whoami)
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=jetsos.service

USER=root
ROOT_DIR=/jetrep

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=JetRep SOS Service
    Documentation=http://jetrep.hzcsai.com
    After=multi-user.target

[Service]
    Type=oneshot
    User=$USER
    Group=$USER
    UMask=0000
    EnvironmentFile=$ROOT_DIR/etc/jetrep.env
    ExecStart=$ROOT_DIR/scripts/jetrep_recovery.sh

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE
cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
systemctl daemon-reload
if [[ x$1 == x1 ]]
then
    # systemctl enable $SERVICE
    # systemctl start $SERVICE
    systemctl status $SERVICE
fi
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
