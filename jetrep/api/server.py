#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file server.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 16:15

import sys
import argparse
import zerorpc

from flask import Flask
from flask_cors import CORS
from gevent import pywsgi
from jetrep.api.routers import srs, systemd

app = Flask('JetRep::Apiserver')
app.debug = True
CORS(app, supports_credentials=True)

app.register_blueprint(systemd, url_prefix="/apis/systemd/v1")
app.register_blueprint(srs, url_prefix="/apis/srs/v1")


@app.route('/')
def homepage():
    return 'Hello World!'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--host',
            default='0.0.0.0',
            type=str,
            dest='host',
            help="host to run jetrep api service")
    parser.add_argument(
            '--port',
            default=8282,
            type=int,
            dest='port',
            help="port to run jetrep api service")
    parser.add_argument(
            '--rpc_host',
            default='0.0.0.0',
            type=str,
            dest='rpc_host',
            help="rpc host")
    parser.add_argument(
            '--rpc_port',
            default=8181,
            type=int,
            dest='rpc_port',
            help="rpc port")

    args = parser.parse_args()

    try:
        app.jetrep = zerorpc.Client(
            timeout=3,
            passive_heartbeat=True)
        ret = app.jetrep.connect('tcp://{}:{}'.format(args.rpc_host, args.rpc_port))  # noqa
        if len(ret) == 0 or ret[0] is None:
            raise RuntimeError('Connect jetrep zerorpc error')
        server = pywsgi.WSGIServer((args.host, args.port), app)
        server.serve_forever()
    except Exception as err:
        sys.stderr.write(f'{err}\n')
    finally:
        pass
