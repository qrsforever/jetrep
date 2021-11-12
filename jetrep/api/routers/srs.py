#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file srs.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 17:49

import json
from flask import Blueprint, request, Response # noqa
from flask import current_app as app

srs = Blueprint("srs", __name__)

OK = "0" # Response(status=200, headers={})


@srs.route('/on_connect', methods=['POST', 'PUT'])
def _srs_on_connect():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_close', methods=['POST'])
def _srs_on_close():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_publish', methods=['POST'])
def _srs_on_publish():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_unpublish', methods=['POST'])
def _srs_on_unpublish():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_play', methods=['POST'])
def _srs_on_play():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_stop', methods=['POST'])
def _srs_on_stop():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_dvr', methods=['POST'])
def _srs_on_dvr():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_hls', methods=['POST'])
def _srs_on_hls():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@srs.route('/on_hls_notify', methods=['GET'])
def _srs_on_hls_notify():
    app.logger.info(request.args)
    return OK
