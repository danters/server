#!/bin/bash

handle_error() {
    echo "FAILED: line $1, exit code $2"
#    exit 1
}

trap 'handle_error $LINENO $?' ERR 


kill -9 $(ps aux | grep [H]Rest.py | grep -v grep | awk '{print $2}')
kill -9 $(ps aux | grep [m]essageClient.py | grep -v grep | awk '{print $2}')
kill -9 $(ps aux | grep [H]WsServer.py | grep -v grep | awk '{print $2}')


