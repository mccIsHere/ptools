opt=$1

#pidfile="cur.pid"

shome="${HOME}/static_web/content"
cd $shome

ts=$(date +%Y.%m.%d_%H.%M)

port="8000"
scmd="python -m SimpleHTTPServer ${port}"

case ${opt} in
    "on")
	echo 'Starting Server..'
	${scmd}  >"${shome}/../logs/out.${ts}.txt" 2>"${shome}/../logs/err.${ts}.txt" &
	echo $(hostname)":${port}"
	;;
    "off")
	echo 'Stopping Server..'
	pkill -15 -f "${scmd}"
	;;
    "re")
	echo 'Restarting Server..'
	sh $0 off
	sleep 2
	sh $0 on
	;;
    *)
	echo 'Unknown option. Use: on/off/re'
	exit
	;;
esac
