#!/bin/bash

services=('jetapi' 'jetsrs' 'jetgst' 'jetrep')

if [[ 0 != $(whoami) ]]
then
    XRUN=sudo
fi

for s in ${services[@]}
do
    if [[ x$1 == x1 && $s == jetrep ]]
    then
        continue
    fi
    alive=`systemctl is-active $s`
    if [[ $alive == active ]]
    then
        $XRUN systemctl stop $s
    fi
done

for pid in `ps -eo pid,args | grep "c from multiprocessing" | cut -c1-6`
do
    $XRUN kill -9 $pid 2>/dev/null
done

exit 0
