#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file jetrep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 21:01

import sys, os, signal, traceback # noqa
import logging, time
import traitlets
import multiprocessing
from multiprocessing import Queue
from logging.handlers import RotatingFileHandler
from traitlets.config.application import Application
from traitlets import Bool, Int, Unicode, List, Dict, Enum # noqa
from jetrep.core.message import MessageHandler
from jetrep.core.message import MainHandlerThread, LogHandlerThread
from jetrep.core.message import (
    MessageType,
    CommandType,
    LogType,
)
from jetrep.core.handlers import (
    LogHandler,
    StateHandler,
    DefaultHandler
)
from jetrep.core.tasks import (
    ServiceRPC,
    InferProcessRT,
    PreProcessRep,
    PostProcessRep,
)
from jetrep.utils.shell import (
    util_check_service,
    util_start_service,
    util_stop_service
)
from jetrep.core import PSContext


multiprocessing.set_start_method('forkserver', force=True)
# multiprocessing.set_start_method('spawn', force=True)


class NativeHandler(MessageHandler):
    def __init__(self, app, log_handler):
        super(NativeHandler, self).__init__(app)
        self.log_handler = log_handler

    def handle_message(self, what, arg1, arg2, obj):
        pass

    def logd(self, s):
        self.log_handler.send_message(MessageType.LOG, LogType.DEBUG, obj=f'{s}')

    def logi(self, s):
        self.log_handler.send_message(MessageType.LOG, LogType.INFO, obj=f'{s}')

    def logw(self, s):
        self.log_handler.send_message(MessageType.LOG, LogType.WARNING, obj=f'{s}')

    def loge(self, s):
        self.log_handler.send_message(MessageType.LOG, LogType.ERROR, obj=f'{s}')


class JetRepApp(Application):
    """
    This is a repnet run on the jetson nano application.
    """
    name = Unicode('JetRepApp')
    description = Unicode(__doc__)

    svc_name_repapi = Unicode('repapi', read_only=True)
    svc_name_jetgst = Unicode('jetgst', read_only=True)
    svc_name_srsrtc = Unicode('srsrtc', read_only=True)
    tsk_name_engine = Unicode('engine', read_only=True)
    tsk_name_prerep = Unicode('prerep', read_only=True)
    tsk_name_postrep = Unicode('postrep', read_only=True)

    config_file = Unicode('', help='Load this config file').tag(config=True)
    log_file = Unicode('/tmp/jetrep.log', help='Write log to file ').tag(config=True)

    rpc_ip = Unicode('127.0.0.1', help='Set zerorpc host').tag(config=True)
    rpc_port = Int(8181, help='Set zerorpc port').tag(config=True)

    classes = List([PSContext])

    aliases = Dict(
        dict(
            c='JetRepApp.config_file',
            addr='JetRepApp.rpc_ip',
            port='JetRepApp.rpc_port'
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

        # def thread_id_filter(record):
        #     record.thread_id = threading.get_native_id()
        #     return record

        formatter = self._log_formatter_cls(fmt=self.log_format, datefmt=self.log_datefmt)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        # console.addFilter(thread_id_filter)

        filelog = RotatingFileHandler(
                self.log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
        filelog.setFormatter(formatter)
        # filelog.addFilter(thread_id_filter)

        log.addHandler(console)
        log.addHandler(filelog)
        return log

    def initialize(self, argv=None):
        self.parse_command_line(argv)
        if self.config_file:
            self.load_config_file(self.config_file)
        print(self.print_options())

    def setup(self):
        self.log_looper = LogHandlerThread()
        self.main_looper = MainHandlerThread()

        StateHandler.instance(self)
        DefaultHandler.instance(self)

        self.native = NativeHandler(self, LogHandler.instance(self))

        self.log.info('Setup Rpc server')
        self.rpc_task = ServiceRPC(self, self.rpc_ip, self.rpc_port)

        self.log.info('Setup Trt Engine')
        self.mq_in, self.mq_out, self.psctx = Queue(), Queue(), PSContext()
        self.trt_engine_task = InferProcessRT(self, self.rpc_ip, self.rpc_port, self.mq_in, self.mq_out)
        self.trt_prerep_task = PreProcessRep(self, self.mq_in, self.mq_out)
        self.trt_postrep_task = PostProcessRep(self, self.mq_in, self.mq_out)

    def start(self):
        self.log.info('Starting...')
        self.log_looper.start()
        self.main_looper.start()
        self.rpc_task.start()
        self.native.send_message(MessageType.CTRL, CommandType.APP_START)

    def stop(self):
        self.log.info('Stopping...')
        self.native.send_message(MessageType.CTRL, CommandType.APP_STOP)
        for _ in range(20):
            result = self.status()
            self.log.info(f'Status: [{result}]')
            if not any(list(result.values())):
                break
            time.sleep(1)
        self.rpc_task.stop()

    def status(self):
        status = {}
        status[self.svc_name_jetgst] = util_check_service(self.svc_name_jetgst)
        status[self.svc_name_srsrtc] = util_check_service(self.svc_name_srsrtc)
        status[self.svc_name_repapi] = util_check_service(self.svc_name_repapi)

        status[self.tsk_name_engine] = self.trt_engine_task.is_alive() if self.trt_engine_task else False
        status[self.tsk_name_prerep] = self.trt_prerep_task.is_alive() if self.trt_prerep_task else False
        status[self.tsk_name_postrep] = self.trt_postrep_task.is_alive() if self.trt_postrep_task else False
        return status

    def start_trt_postrep(self):
        self.log.info('Start Trt PostRep')
        self.trt_postrep_task.start()
        return True

    def stop_trt_postrep(self):
        self.log.info('Stop Trt PostRep')
        self.trt_postrep_task.stop()
        return True

    def start_trt_prerep(self):
        self.log.info('Start Trt PreRep')
        self.trt_prerep_task.start()
        return True

    def stop_trt_prerep(self):
        self.log.info('Stop Trt PreRep')
        self.trt_prerep_task.stop()
        return True

    def start_trt_engine(self):
        self.log.info('Start Trt Engine')
        self.trt_engine_task.start()
        return True

    def stop_trt_engine(self):
        self.log.info('Stop Trt Engine')
        self.trt_engine_task.stop()
        return True

    def start_gst_launch(self):
        self.log.info('Start Gst Launch')
        if util_check_service(self.svc_name_jetgst):
            util_stop_service(self.svc_name_jetgst)
        return not util_start_service(self.svc_name_jetgst)

    def stop_gst_launch(self):
        self.log.info('Stop Gst Launch')
        return not util_stop_service(self.svc_name_jetgst) \
                if util_check_service(self.svc_name_jetgst) else True

    def start_srs_webrtc(self):
        self.log.info('Start Srs Webrtc')
        return not util_start_service(self.svc_name_srsrtc, True)

    def stop_srs_webrtc(self):
        self.log.info('Stop Srs Webrtc')
        return not util_stop_service(self.svc_name_srsrtc) \
                if util_check_service(self.svc_name_srsrtc) else True

    def start_api_handler(self):
        self.log.info('Start Api Handler')
        return not util_start_service(self.svc_name_repapi, True)

    def stop_api_handler(self):
        self.log.info('Stop Api Handler')
        return not util_stop_service(self.svc_name_repapi) \
                if util_check_service(self.svc_name_repapi) else True

    def run(self, argv=None):
        try:
            self.initialize(argv)
            self.setup()
            self.start()
            self.rpc_task.join()
            self.trt_engine_task.join()
            self.trt_prerep_task.join()
            self.trt_postrep_task.join()
        except Exception:
            self.log.error(traceback.format_exc(limit=6))
            os._exit(os.EX_OK)


def signal_handler(sig, frame):
    app.log.info('JetRepApp handle signal: [%d]' % sig)
    app.stop()
    os._exit(os.EX_OK)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    app = JetRepApp()
    app.run()
