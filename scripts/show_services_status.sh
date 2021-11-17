#!/bin/bash

services=('repapi' 'srsrtc' 'jetgst' 'jetrep')

N=$1

if [[ x$N == x ]]
then
    N=20
fi

clear

for s in ${services[@]}
do
    systemctl status $s -n 0
    echo -e "\n-----------------------------------------------------------------------------------------\n"
    journalctl -u $s --no-pager -n $N
    echo -e "========================  journalctl -u $s --no-pager -n $N  ============================\n\n"
done
