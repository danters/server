#!/bin/bash

handle_error() {
    echo "FAILED: line $1, exit code $2"
#    exit 1
}

trap 'handle_error $LINENO $?' ERR 

sleep 2
nohup ./../HWsServer.py 0 > ./../logs/ws.log &
nohup ./../messageClient.py 0  > ./../logs/msg.log &
nohup ./../HRest.py 0  > ./../logs/rest.log &

