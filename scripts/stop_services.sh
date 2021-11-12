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
