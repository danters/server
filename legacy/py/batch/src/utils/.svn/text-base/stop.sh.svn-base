if [ $1 == "rest" ]
then
    echo "Stopping HRest.py"
    kill -9 $(ps aux | grep [H]Rest.py | grep -v grep | awk '{print $2}')
fi

if [ $1 == "msg" ]
then
    echo "Stopping messageClient.py"
    kill -9 $(ps aux | grep [m]essageClient.py | grep -v grep | awk '{print $2}')
fi

if [ $1 == "ws" ]
then
    echo "Stopping HWsServer.py"
    kill -9 $(ps aux | grep [H]WsServer.py | grep -v grep | awk '{print $2}')
fi