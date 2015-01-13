if [ $1 == "rest" ]
then
    echo "Starting HRest.py"
    nohup ./../HRest.py  > ./../logs/rest.log &
fi

if [ $1 == "msg" ]
then
    echo "Starting messageClient.py"
    nohup ./../messageClient.py  > ./../logs/msg.log &
fi

if [ $1 == "ws" ]
then
    echo "Starting HWsServer.py"
    nohup ./../HWsServer.py > ./../logs/ws.log &
fi