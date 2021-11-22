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

from jetrep.utils.net import util_check_port
from flask import Flask, Response, redirect, request # noqa
from flask_cors import CORS
from gevent import pywsgi
from gevent import signal
from jetrep.api.routers import (
    api_srs,
    api_svc,
    api_sys,
    api_rep,
    api_cron,
)
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)

app = Flask('JetRep::Apiserver')
app.debug = True
CORS(app, supports_credentials=True)

app.register_blueprint(api_svc, url_prefix='/apis/svc')
app.register_blueprint(api_srs, url_prefix='/apis/srs')
app.register_blueprint(api_sys, url_prefix='/apis/sys')
app.register_blueprint(api_rep, url_prefix='/apis/rep')

app.register_blueprint(api_cron, url_prefix='/apis/cron')


@app.route('/')
def homepage():
    return 'Hello, Jetson Repnet!'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--host',
            default='127.0.0.1',
            type=str,
            dest='host',
            help="host to run jetrep api service")
    parser.add_argument(
            '--port',
            default=80,
            type=int,
            dest='port',
            help="port to run jetrep api service")
    parser.add_argument(
            '--rpc_host',
            default='127.0.0.1',
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

    def send_message(jet, what, arg1, arg2, obj):
        try:
            app.logger.info(f'({what}, {arg1}, {arg2}, {obj})')
            return jet.send_message(what, arg1, arg2, obj)
        except zerorpc.exceptions.TimeoutExpired:
            app.logger.warning(f'Call send_message timeout!\n')

    try:
        remote = None
        if util_check_port(args.rpc_port, args.rpc_host, trycnt=3):
            remote = zerorpc.Client(
                connect_to='tcp://{}:{}'.format(args.rpc_host, args.rpc_port),
                timeout=10,
                passive_heartbeat=True)
            remote.send_message(MessageType.STATE, ServiceType.API, StateType.STARTED, 'repapi')
            app.remote = remote

            server = pywsgi.WSGIServer((args.host, args.port), app)

            def shutdown(num, frame):
                remote.send_message(MessageType.STATE, ServiceType.API, StateType.STOPPED, 'repapi')
                server.stop()
                remote.close()
                sys.stderr.write('End!!!\n')
                sys.stderr.flush()
                exit(0)

            signal.signal(signal.SIGTERM, shutdown)
            signal.signal(signal.SIGINT, shutdown)
            server.serve_forever()
        else:
            sys.stderr.write(f'Cannot connect to {args.rpc_host}:{args.rpc_port}!\n')
    # except (KeyboardInterrupt, SystemExit):
    except Exception as err:
        sys.stderr.write(f'{err}!\n')
    finally:
        if remote and server.started:
            shutdown()
