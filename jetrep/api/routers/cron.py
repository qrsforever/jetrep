#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file cron.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-22 11:33


from flask import Blueprint, request, Response # noqa
from flask import current_app as app
from jetrep.core.message import (
    MessageType,
    TimerType,
)

api_cron = Blueprint("cron", __name__)

OK = Response(status=200, headers={})


@api_cron.route('/check_disk', methods=['POST'])
def _check_disk():
    reqjson = request.get_json()
    app.logger.info(reqjson)
    return OK


@api_cron.route('/check_update', Methods=['GET'])
def _check_update():
    app.remote.send_message(MessageType.TIMER, TimerType.CHECK_UPDATE, 0)
    return OK
