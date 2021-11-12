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
from gevent import signal
from jetrep.api.routers import srs, systemd
from jetrep.utils.net import util_check_port
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)

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
            default='127.0.0.1',
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
        jetrep = None
        if util_check_port(args.rpc_port, args.rpc_host, trycnt=3):
            jetrep = zerorpc.Client(
                connect_to='tcp://{}:{}'.format(args.rpc_host, args.rpc_port),
                timeout=10,
                passive_heartbeat=True)
            app.send_message = lambda *args, **kwargs: send_message(jetrep, *args, **kwargs)
            app.send_message(MessageType.STATE, ServiceType.API, StateType.STARTING, 'repapi')

            server = pywsgi.WSGIServer((args.host, args.port), app)

            def shutdown(num, frame):
                app.send_message(MessageType.STATE, ServiceType.API, StateType.STOPPING, 'repapi')
                server.stop()
                jetrep.close()
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
        if jetrep and server.started:
            shutdown()
