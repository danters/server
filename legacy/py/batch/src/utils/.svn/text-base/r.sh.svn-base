if [ $1 == "rest" ]
then
    echo "Stopping HRest.py"
    kill -9 $(ps aux | grep [H]Rest.py | grep -v grep | awk '{print $2}')
    sleep 2
    echo "Starting HRest.py"
    nohup ./../HRest.py  > ./../logs/rest.log &
fi

if [ $1 == "msg" ]
then
    echo "Stopping messageClient.py"
    kill -9 $(ps aux | grep [m]essageClient.py | grep -v grep | awk '{print $2}')

    sleep 2
    echo "Starting messageClient.py"
    nohup ./../messageClient.py  > ./../logs/msg.log &
fi

if [ $1 == "ws" ]
then
    echo "Stopping HWsServer.py"
    kill -9 $(ps aux | grep [H]WsServer.py | grep -v grep | awk '{print $2}')

    sleep 2
    echo "Starting HWsServer.py"
    nohup ./../HWsServer.py > ./../logs/ws.log &
fi