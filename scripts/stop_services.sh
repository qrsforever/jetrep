#!/bin/bash

services=('repapi' 'srsrtc' 'jetgst')

N=$1

if [[ x$N == x ]]
then
    N=10
fi

XRUN=

if [[ 0 != $(whoami) ]]
then
    XRUN=sudo
fi

for s in ${services[@]}
do
    $XRUN systemctl stop $s
done

for pid in `ps -eo pid,args | grep "python3 -c from multiprocessing" | cut -c1-6`
do
    $XRUN kill -9 $pid 2>/dev/null
done

exit 0
