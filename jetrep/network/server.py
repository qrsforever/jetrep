#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-25 18:00

import sys, signal, logging
from logging.handlers import RotatingFileHandler
from flask import Flask, Response, redirect, request # noqa
from flask_cors import CORS
from gevent import pywsgi
from jetrep.constants import DefaultPath as DP
from monitor import ConnectMonitor # noqa
from wifi import WifiAP


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


if __name__ == "__main__":
    formatter = logging.Formatter('%(asctime)s - %(funcName)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s')
    file_log = RotatingFileHandler(
            DP.NETWORK_MODULE_LOGFILE, mode='a', maxBytes=5*1024*1024, backupCount=5, encoding=None, delay=0)
    file_log.setFormatter(formatter)
    file_log.setLevel(logging.DEBUG)
    app.logger.addHandler(file_log)
    wifi_ap = WifiAP(app.logger)

    def _on_connect():
        app.logger.warning('net_on_connect')
        wifi_ap.stop()

    def _on_disconnect():
        app.logger.warning('net_on_disconnect')
        wifi_ap.start()

    # monitor = ConnectMonitor(app.logger, _on_connect, _on_disconnect)
    # monitor.start()
    import time
    _on_disconnect()
    time.sleep(3)
    _on_connect()
    time.sleep(5)
    _on_disconnect()
    time.sleep(20)

    server = pywsgi.WSGIServer(('0.0.0.0', 6666), app)

    def shutdown(num, frame):
        if gWifiAP:
            gWifiAP.stop()
        sys.stderr.write('End!!!\n')
        sys.stderr.flush()
        exit(0)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    server.serve_forever()
