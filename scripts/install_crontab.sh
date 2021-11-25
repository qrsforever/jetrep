#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
CRONTAB_DIR=/jetrep/etc/crontab

XRUN=
if [[ 0 != $(id -u) ]]
then
    XRUN=sudo
fi

cat > $TOP_DIR/runtime/crontab <<EOF
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

17 *	* * *	root    test -x $CRONTAB_DIR/jetrep.hourly && $CRONTAB_DIR/jetrep.hourly

@reboot root test -x $CRONTAB_DIR/reboot && $CRONTAB_DIR/reboot
EOF

$XRUN cp $TOP_DIR/runtime/crontab /etc/crontab
