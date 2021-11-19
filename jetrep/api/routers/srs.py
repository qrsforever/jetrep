#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file srs.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 17:49

import json
from jetrep.utils.net import util_get_lanip
from jetrep.utils.misc import DotDict
from flask import Blueprint, request, Response # noqa
from flask import current_app as app

api_srs = Blueprint("srs", __name__)

OK = "0" # Response(status=200, headers={})

_Client_Caches_ = {}


@api_srs.route('/streams')
def _srs_streams_list():
    srsip = util_get_lanip()
    html = '<html><body><b><p>Streams</p></b><ul>'
    for client_id, player_url in _Client_Caches_.items():
        player_url = player_url.replace('0.0.0.0', srsip).replace('127.0.0.1', srsip)
        html += f'<li><a href={player_url}>{player_url}</a></li>'
    html += '</ul></body></html>'
    return html


@api_srs.route('/on_connect', methods=['POST', 'PUT'])
def _srs_on_connect():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    r = DotDict(reqjson)
    if r.vhost.startswith('jet'):
        page = 'rtc_player.html'
        suffix = ''
    else:
        page = 'srs_player.html'
        suffix = '.m3u8'
    player_url = f'http://127.0.0.1:8080/players/{page}?vhost={r.vhost}&app={r.app}&stream={r.stream}{suffix}&autostart=true'
    _Client_Caches_[r.client_id] = player_url
    return OK


@api_srs.route('/on_close', methods=['POST'])
def _srs_on_close():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    r = DotDict(reqjson)
    if r.client_id in _Client_Caches_:
        _Client_Caches_.pop(r.client_id)
    return OK


@api_srs.route('/on_publish', methods=['POST'])
def _srs_on_publish():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@api_srs.route('/on_unpublish', methods=['POST'])
def _srs_on_unpublish():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@api_srs.route('/on_play', methods=['POST'])
def _srs_on_play():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@api_srs.route('/on_stop', methods=['POST'])
def _srs_on_stop():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@api_srs.route('/on_dvr', methods=['POST'])
def _srs_on_dvr():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    # {
    #     "action": "on_dvr",
    #     "client_id": 156,
    #     "ip": "36.110.84.59",
    #     "vhost": "seg.30s",
    #     "app": "f01",
    #     "stream": "00e685ef87b4",
    #     "param": "?vhost=seg.30s",
    #     "cwd": "/usr/local/srs",
    #     "file": "/frepai/data/f01/00e685ef87b4/20210629170921.mp4"
    # }
    # basefile = os.path.basename(reqjson['file'])
    # localfile = os.path.join(reqjson['cwd'], reqjson['file'])
    return OK


@api_srs.route('/on_hls', methods=['POST'])
def _srs_on_hls():
    reqjson = json.loads(request.get_data().decode())
    app.logger.info(reqjson)
    return OK


@api_srs.route('/on_hls_notify', methods=['GET'])
def _srs_on_hls_notify():
    app.logger.info(request.args)
    return OK
