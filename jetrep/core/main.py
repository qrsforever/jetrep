#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file jetrep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 21:01

import sys, os, signal, traceback # noqa
import logging, time
import zerorpc
from logging.handlers import RotatingFileHandler
import traitlets
from traitlets.config.application import Application
from traitlets import Bool, Int, Unicode, List, Dict, Enum # noqa

from jetrep.core.message import MessageHandler as MH
from jetrep.core.message import MessageType as MT # noqa
from jetrep.core.message import MainHandlerThread
from jetrep.core.handlers import (
    LogHandler,
    StateHandler,
    DefaultHandler
)
from jetrep.utils.shell import (
    util_check_service,
    util_start_service,
    util_stop_service
)


class NativeHandler(MH):
    def __init__(self, app):
        super(NativeHandler, self).__init__(app)

    def handle_message(self, what, arg1, arg2, obj):
        pass


class JetRepApp(Application):
    """
    This is a repnet run on the jetson nano application.
    """
    name = Unicode('JetRepApp')
    description = Unicode(__doc__)
    service_repapi = Unicode('repapi', read_only=True)
    service_jetgst = Unicode('jetgst', read_only=True)
    service_srsrtc = Unicode('srsrtc', read_only=True)
    config_file = Unicode('', help='Load this config file').tag(config=True)
    log_file = Unicode('/tmp/jetrep.log', help='Write log to file ').tag(config=True)
    rpc_host = Unicode('127.0.0.1', help='Set zerorpc host').tag(config=True)
    rpc_port = Int(8181, help='Set zerorpc port').tag(config=True)

    classes = List([])

    aliases = Dict(
        dict(
            c='JetRepApp.config_file'
        )
    )

    flags = Dict(
        dict(
            debug=({'JetRepApp': {'log_level': 10}}, 'Set loglevel to DEBUG'),
        )
    )

    @traitlets.default('log')
    def _log_default(self):
        log = logging.getLogger(self.__class__.__name__)
        log.setLevel(self.log_level)
        formatter = self._log_formatter_cls(fmt=self.log_format, datefmt=self.log_datefmt)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        filelog = RotatingFileHandler(
                self.log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
        filelog.setFormatter(formatter)
        log.addHandler(console)
        log.addHandler(filelog)
        return log

    def initialize(self, argv=None):
        self.parse_command_line(argv)
        if self.config_file:
            self.load_config_file(self.config_file)

    def setup(self):
        self.looper = MainHandlerThread()
        self.native = NativeHandler(self)

        LogHandler.instance(self)
        StateHandler.instance(self)
        DefaultHandler.instance(self)

        self.server = zerorpc.Server(self.native)
        self.server.bind(f'tcp://{self.rpc_host}:{self.rpc_port}')

    def start(self):
        self.log.info('Starting...')
        self.looper.start()
        self.native.send_message(MessageType.CTRL)

    def stop(self):
        self.log.info('Stopping...')
        self.stop_gst_launch()
        for _ in range(10):
            result = self.status()
            self.log.info(f'Status: [{result}]')
            if not any(list(result.values())):
                break
            time.sleep(1)
        self.stop_api_handler()
        self.server.stop()

    def status(self):
        status = {}
        status[self.service_jetgst] = util_check_service(self.service_jetgst)
        status[self.service_srsrtc] = util_check_service(self.service_srsrtc) 
        status[self.service_repapi] = util_check_service(self.service_repapi)
        return status

    def start_gst_launch(self):
        self.log.info('Start Gst Launch')
        if util_check_service(self.service_jetgst):
            util_stop_service(self.service_jetgst)
        return not util_start_service(self.service_jetgst)

    def stop_gst_launch(self):
        self.log.info('Stop Gst Launch')
        return not util_stop_service(self.service_jetgst) \
                if util_check_service(self.service_jetgst) else True

    def start_srs_webrtc(self):
        self.log.info('Start Srs Webrtc')
        return not util_start_service(self.service_srsrtc, True)

    def stop_srs_webrtc(self):
        self.log.info('Stop Srs Webrtc')
        return not util_stop_service(self.service_srsrtc) \
                if util_check_service(self.service_srsrtc) else True

    def start_api_handler(self):
        self.log.info('Start Api Handler')
        return not util_start_service(self.service_repapi, True)

    def stop_api_handler(self):
        self.log.info('Stop Api Handler')
        return not util_stop_service(self.service_repapi) \
                if util_check_service(self.service_repapi) else True

    def run(self, argv=None):
        try:
            self.initialize(argv)
            self.setup()
            self.start()
            self.server.run()
        except Exception:
            self.log.error(traceback.format_exc(limit=6))
            os._exit(os.EX_IOERR)


def signal_handler(sig, frame):
    app.log.info('JetRepApp handle signal: [%d]' % sig)
    app.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    app = JetRepApp()
    app.run()
