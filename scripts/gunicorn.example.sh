#!/bin/bash
set -e
# start config
APPNAME=verese
INSTANCE="dev"
NUM_WORKERS=4
# end config

USERDIR=`grep $USERNAME /etc/passwd | cut -d ":" -f6`
LOGFILE="$USERDIR/logs/$INSTANCE/gunicorn.log"
SOCKET="unix:$USERDIR/sockets/$INSTANCE/verese.sock"

cd $USERDIR/$INSTANCE
source ./env/bin/activate
exec ./env/bin/gunicorn_django -w $NUM_WORKERS \
    --log-level=info --log-file=$LOGFILE --bind $SOCKET 2l>> $LOGFILE verese/settings.py
