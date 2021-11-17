#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file sys.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-17 16:16

import json
from flask import Blueprint, request, Response
from flask import current_app as app

api_sys = Blueprint("sys", __name__)

OK = Response(status=200, headers={})
ERR = Response(status=500, headers={})


@api_sys.route('/ota', methods=['POST'])
def _sys_ota():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK
