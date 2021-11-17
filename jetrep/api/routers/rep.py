#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file rep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-17 16:21


import json
from flask import Blueprint, request, Response
from flask import current_app as app
from jetrep.core.message import (
    MessageType,
    CommandType,
)
from jetrep.constants import JPath

api_rep = Blueprint("rep", __name__)

OK = Response(status=200, headers={})
ERR = Response(status=500, headers={})


@api_rep.route('/set_param', methods=['POST'])
def _rep_set_param():
    reqjson = request.get_json()
    app.logger.info(reqjson)
    with open(JPath.JETREP_CONF_PATH, 'w') as fw:
        fw.write(json.dumps(reqjson, indent=4))
    app.remote.send_message(MessageType.CTRL, CommandType.API_SET_PARAM, -1, JPath.JETREP_CONF_PATH)
    return OK
