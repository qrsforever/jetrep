## Alias

alias jcurl='curl --header  "Content-Type: application/json" --request POST --data '
alias jrun='sudo systemctl restart jetrep.service'
alias jstop='sudo systemctl stop jetrep.service'
alias jlog='clear; journalctl --no-page -u jetrep -u jetapi -u jetsrs -u jetgst -f -n 100'
alias jrunlog='clear; sudo systemctl restart jetrep.service; journalctl -u jetrep -u jetapi -u jetpsrs -u jetgst -f -n 100'
alias journalctl='journalctl --no-page'

## Video

gst-launch-1.0 -e videotestsrc ! queue ! videoconvert ! x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! flvmux streamable=true ! queue ! rtmpsink location=http://0.0.0.0:1935/live/13


## curl

export IP1=172.16.0.17
export IP2=192.168.45.1
export IP3=172.16.2.209

### connect wifi

curl --header  "Content-Type: application/json" --request POST --data  '{"ssid": "国电社区", "password": "88888888"}' http://$IP2/apis/rep/wifi_connect

### update check

curl --request GET http://$IP1/apis/cron/check_update 
