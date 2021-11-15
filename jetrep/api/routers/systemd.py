#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file systemd.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 17:53

import json
from flask import Blueprint, request, Response
from flask import current_app as app
from jetrep.core.message import (
    MessageType,
    StateType,
    ServiceType,
    LogType
)

systemd = Blueprint("systemd", __name__)

OK = Response(status=200, headers={})
ERR = Response(status=500, headers={})

SER_STR2INT = {
    'repapi': ServiceType.API,
    'srsrtc': ServiceType.SRS,
    'jetgst': ServiceType.GST,
}

STA_STR2INT = {
    'starting': StateType.STARTING,
    'stopping': StateType.STOPPING,
    'started': StateType.STARTED,
    'stopped': StateType.STOPPED,
}


@systemd.route('/status', methods=['POST'])
def _systemd_status():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    sname = reqjson['name']
    state = reqjson['status']
    app.remote.logi(reqjson)
    if sname not in SER_STR2INT or state not in STA_STR2INT:
        app.logger.warning(f'Not support service name [{sname}] and state [{state}]')
        return ERR
    app.remote.send_message(MessageType.STATE, SER_STR2INT[sname], STA_STR2INT[state], sname)
    return OK
