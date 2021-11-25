#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-25 18:00


from flask import Flask, Response, redirect, request # noqa
from flask_cors import CORS
from gevent import pywsgi
from .monitor import ConnectMonitor
from .wifi import WifiAP


gWifiAP = None
app = Flask('JetNet')
app.debug = True
CORS(app, supports_credentials=True)


@app.route('/wifi_list')
def _wifi_list():
    return '0'


@app.route('/wifi_connect')
def _wifi_connect():
    pass


def net_on_connect():
    app.logger.warning('net_on_connect')
    global gWifiAP
    if gWifiAP:
        gWifiAP.kill()
    gWifiAP = WifiAP()
    gWifiAP.start()


def net_on_disconnect():
    app.logger.warning('net_on_disconnect')
    if gWifiAP:
        gWifiAP.kill()


if __name__ == "__main__":
    monitor = ConnectMonitor(app.logger, net_on_connect, net_on_disconnect)
    monitor.start()
    app.wifiap = None
    server = pywsgi.WSGIServer(('0.0.0.0', 6666), app)
    server.serve_forever()
