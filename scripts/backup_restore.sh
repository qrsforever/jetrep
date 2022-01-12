#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

DEV=/dev/sdc

if [[ x$(which dump) == x ]]
then
    sudo apt install dump
fi

## Backup
if [[ x$1 == x1 ]]
then
    parts=()
    while read line
    do
        if [[ ${line:0:8} == "$DEV" ]]
        then
            cid=`echo ${line:8:2} | awk '{print int($0)}'`
            ret=`echo $line | cut -d\  -f2-3`
            parts[$cid]="$ret"
        fi
    done < <(sudo fdisk -l $DEV)

    while read line
    do
        cid=`echo $line | cut -d\  -f1`
        if [[ "$cid" =~ ^[0-9]+$ ]]
        then
            label=`echo $line | cut -d\  -f5-`
            parts[$cid]="${parts[$cid]} $label"
        fi
    done < <(sudo parted -s $DEV print)

    rm -f parts.txt 2>/dev/null

    for idx in `seq 1 ${#parts[@]}`
    do
        echo "${parts[$idx]}" >> parts.txt
    done

    echo "Backup"
    if [[ ! -d images ]]
    then
        mkdir images
    fi

    ret=`df --output="target" ${DEV}1`
    if [[ "${ret:0:7}" != "Mounted" ]]
    then
        echo "Error: ${DEV} not mounted!"
        exit 0
    fi

    for idx in `seq 2 ${#parts[@]}`
    do
        label=`echo ${parts[$idx]} | cut -d\  -f3`
        sudo dd if=${DEV}${idx} of=$CUR_DIR/images/${idx}_$label.img
    done

    mountpoint=`echo $ret | cut -d\  -f3`
    # sudo dump -0uj -f images/1_app.bz2 $mountpoint
    echo "sudo dump -0uj -f images/1_APP.bz2 $mountpoint"
fi

## Restore
if [[ x$1 == x2 ]]
then
    echo "Restore"
    sudo umount ${DEV}1 2>/dev/null
    sudo umount ${DEV}1 2>/dev/null
    while read line
    do
        cid=`echo $line | cut -d\  -f1`
        if [[ "$cid" =~ ^[0-9]+$ ]]
        then
            # remove partitions
            sudo parted -s $DEV rm $cid
            echo "sudo parted -s $DEV rm $cid"
        fi
    done < <(sudo parted -s $DEV print)
    # sudo fdisk  -l $DEV
    sudo parted $DEV --script -- mklabel GPT

    ss=1
    cat parts.txt | while read line
    do
        s1=`echo $line | cut -d\  -f1`
        if [[ $ss == 1 ]]
        then
            sudo parted --script $DEV mkpart APP ext4 ${s1}s 100%
            sudo mkfs.ext4 -F ${DEV}${ss}
            /bin/rm -rf ./images/sysroot
            mkdir -p ./images/sysroot
            sudo mount -t ext4 ${DEV}${ss} ./images/sysroot
            cd ./images/sysroot
            sudo restore -r -f $CUR_DIR/images/1_APP.bz2
            cd - >/dev/null
            sudo umount ${DEV}${ss}
        else
            s2=`echo $line | cut -d\  -f2`
            s3=`echo $line | cut -d\  -f3`
            sudo parted --script $DEV mkpart ${s3} ${s1}s ${s2}s
            sudo dd of=${DEV}{ss} if=./images/${ss}_${s3}.img
        fi
        (( ss = ss + 1 ))
    done
fi
