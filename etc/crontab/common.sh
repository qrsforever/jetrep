#!/bin/bash

SCRIPTDIR="$(dirname "$0")"

. $SCRIPTDIR/cron.env

if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

##### Debug ######
BASH_DEBUG_LOGFILE=/tmp/jetrep_cron.log
ENABLE_DEBUG=1

debug_check_logfile() {
    if [[ -f $BASH_DEBUG_LOGFILE ]]
    then
        logsize=`stat --printf="%s" $BASH_DEBUG_LOGFILE`
        if [ $logsize -gt 6000000 ]
        then
            mv $BASH_DEBUG_LOGFILE ${BASH_DEBUG_LOGFILE}.bak
        fi
    fi
}

debug_print() {
    if [[ x$ENABLE_DEBUG == x1 ]]
    then
        datestr=`date +"%Y/%m/%d %H:%M:%S"`
        echo $datestr $0 $* >> $BASH_DEBUG_LOGFILE
    fi
}


###### Curl Message ######

curl_post() {
    result=`curl --connect-timeout 3 -s \
        -H "Accept: application/json" \
        -H "Content-Type:application/json" \
        -X POST --data "$1" "$2"`
    retcode=$?
    if [[ x$retcode != x0 ]]
    then
        result="-1"
    fi
    echo $result
}

curl_get() {
    result=`curl --connect-timeout 3 -s \
        -H "Accept: application/json" \
        -X GET "$1"`
    retcode=$?
    if [[ x$retcode != x0 ]]
    then
        result="-1"
    fi
    echo $result
}

msg_report() {
    debug_print "$FUNCNAME" $*
    curl_post "$2" "$CRON_API/$1"
}

timer_reminder() {
    debug_print "$FUNCNAME" $*
    curl_get "$CRON_API/$1"
}

rep_status() {
    debug_print "$FUNCNAME" $*
    curl_get "$JREP_API/status"
}

###### Clean SRS Cache ######

dvr_clean_up() {
    debug_print "$FUNCNAME" $*
    if [[ x$1 != x ]]
    then
        dvr_cache_dir=$1
    else
        dvr_cache_dir=$DVR_CACHE_DIR
    fi
    ddirs=(`ls -r $dvr_cache_dir`)
    if [ ${#ddirs[@]} -gt $DVR_SAVE_DAYS ]
    then
        rmdirs=${ddirs[@]:$DVR_SAVE_DAYS}
    else
        rmdirs=(${ddirs[-1]})
    fi
    unset ddirs
    for dir in ${rmdirs[@]}
    do
        $XRUN rm -rf ${dvr_cache_dir}/$dir
    done
    unset rmdirs
}

debug_check_logfile
