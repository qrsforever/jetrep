#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file jetrep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 21:01

import sys, signal, traceback # noqa
import logging
import zerorpc
from logging.handlers import RotatingFileHandler
import traitlets
from traitlets.config.application import Application
from traitlets import Bool, Int, Unicode, List, Dict, Enum # noqa

from jetrep.core.message import MessageHandler as MH
from jetrep.core.message import MessageType as MT # noqa
from jetrep.core.message import MainHandlerThread
from jetrep.core.handlers import LogHandler
from jetrep.core.handlers import StateHandler
from jetrep.core.handlers import DefaultHandler


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
    config_file = Unicode('', help='Load this config file').tag(config=True)
    log_file = Unicode('/tmp/jetrep.log', help='Write log to file ').tag(config=True)
    rpc_host = Unicode('0.0.0.0', help='Set zerorpc host').tag(config=True)
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

    def start(self):
        self.log.info('Starting...')
        self.looper.start()

    def stop(self):
        self.log.info('Stoped.')

    def run(self, argv=None):
        try:
            self.initialize(argv)
            self.setup()
            self.start()
            server = zerorpc.Server(self.native)
            server.bind(f'tcp:{self.rpc_host}:{self.rpc_port}')
            server.run()
        except Exception:
            self.log.error(traceback.format_exc(limit=6))


if __name__ == "__main__":
    app = JetRepApp()
    app.run()
