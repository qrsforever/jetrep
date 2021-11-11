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

SER_STR2INT = {
    'jetgst': ServiceType.GST,
    'srs': ServiceType.SRS
}

STA_STR2INT = {
    'started': StateType.STARTED,
    'stopped': StateType.STOPPED,
}


@systemd.route('/status', methods=['POST'])
def _systemd_status():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    sname = reqjson['name']
    state = reqjson['status']
    app.jetrep.send_message(MessageType.LOG, LogType.INFO, obj=reqjson)
    if sname not in SER_STR2INT or state not in STA_STR2INT:
        app.logger.warning(f'Not support service name [{sname}] and state [{state}]')
    app.jetrep.send_message(MessageType.STATE, SER_STR2INT[sname], STA_STR2INT[state])
    return OK
