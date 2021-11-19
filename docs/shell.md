alias jcurl='curl --header  "Content-Type: application/json" --request POST --data '
alias jrun='sudo systemctl restart jetrep.service'
alias jlog='journalctl -u jetrep -u repai -u srsrtc -u jetgst -f -n 100'
