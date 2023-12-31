#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file rep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-17 16:21


import json # noqa
import traceback
from flask import Blueprint, request, Response, redirect, url_for, render_template
from flask import current_app as app
from jetrep.core.message import (
    MessageType,
    CommandType,
    NetworkType,
)

api_rep = Blueprint("rep", __name__)

OK = Response(status=200, headers={})
ERR = Response(status=500, headers={})


@api_rep.route('/easyset', methods=['GET'])
def _rep_easyset():
    return render_template('rep_easyset.html')


@api_rep.route('/set_param', methods=['POST'])
def _rep_set_param():
    reqjson = request.get_json()
    app.logger.info(reqjson)
    app.remote.send_message(MessageType.CTRL, CommandType.API_SET_PARAM, -1, reqjson)
    return OK


@api_rep.route('/reset_param', methods=['GET'])
def _rep_reset_param():
    app.remote.send_message(MessageType.CTRL, CommandType.API_RESET_PARAM) 
    return OK


@api_rep.route('/restart', methods=['POST'])
def _rep_reboot():
    reqjson = request.get_json()
    app.logger.info(reqjson)
    if reqjson['username'] == 'jetson' and reqjson['password'] == 'nano':
        app.remote.send_message(MessageType.CTRL, CommandType.APP_RESTART)
    return OK


@api_rep.route('/status', methods=['GET']) # TODO don't modify: see crontab/common.sh
def _rep_status():
    result = app.remote.get_status()
    app.logger.info(result)
    if all(list(result.values())):
        return "1"
    return "0"


@api_rep.route('/wifi_connect', methods=['POST', 'GET'])
def _rep_wifi_connect():
    status, message = 0, 'SUCCESS'
    try:
        if request.method == 'POST':
            if request.form:
                reqjson = {
                    'ssid': request.form['ssid'],
                    'password': request.form['password']
                }
            else:
                reqjson = request.get_json()
        else:
            reqjson = {
                'ssid': request.args.get('ssid'),
                'password': request.args.get('password')
            }
        app.logger.info(reqjson)
        app.remote.send_message(MessageType.NETWORK, NetworkType.WIFI_CONNECT, -1, reqjson)
    except Exception:
        status = -99
        message = traceback.format_exc(limit=4)
    return redirect(url_for('response', status=status, message=message))
