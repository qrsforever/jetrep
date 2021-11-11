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

systemd = Blueprint("systemd", __name__)

OK = Response(status=200, headers={})


@systemd.route('/status', methods=['POST'])
def _systemd_status():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK
