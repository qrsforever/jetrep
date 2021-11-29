#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file jetrep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 21:01

import sys, os, signal, traceback # noqa
import logging, time, json
import shutil
import traitlets
import multiprocessing
from multiprocessing import Event, Queue
from logging.handlers import RotatingFileHandler
from traitlets.config.application import Application
from traitlets import Bool, Int, Unicode, List, Dict, Enum # noqa
from jetrep.core.message import MessageHandler
from jetrep.core.message import MainHandlerThread, LogHandlerThread
from jetrep.core.message import (
    MessageType,
    CommandType,
    ServiceType,
    NotifyType,
    PayloadType,
    StateType,
    LogType,
)
from jetrep.core.handlers import (
    LogHandler,
    DefaultHandler,
    StateHandler,
    NotifyHandler,
    NetworkHandler,
)
from jetrep.core.tasks import (
    ServiceRPC,
    TRTEngineProcess,
    TRTPrerepProcess,
    TRTPostrepProcess,
)
from jetrep.utils.shell import (
    util_check_service,
    util_start_service,
    util_stop_service
)
from jetrep.core.context import PSContext
from jetrep.core.event import SystemEventMonitor
from jetrep.constants import DefaultPath as DP
from jetrep.utils.misc import MeldDict
from jetrep.core.upgrade import SoftwareUpgrade

multiprocessing.set_start_method('forkserver', force=True)
# multiprocessing.set_start_method('spawn', force=True)


class NativeHandler(MessageHandler):
    def __init__(self, app, log_handler):
        super(NativeHandler, self).__init__(app)
        self.log_handler = log_handler

    def handle_message(self, what, arg1, arg2, obj):
        pass

    def get_props_frame(self): # height, width, rate
        return self.app.psctx.frame_size[0], \
                self.app.psctx.frame_size[1], \
                self.app.psctx.frame_rate

    def get_status(self):
        return self.app.status()

    def get_bucket(self):
        return self.app.psctx.make_bucket()

    def logd(self, s, remote=False):
        if not remote:
            filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
            lineno = sys._getframe().f_back.f_lineno
            s = f'[{os.getpid()}] {filename}:{lineno} --> {s}'
        self.log_handler.send_message(MessageType.LOG, LogType.DEBUG, obj=f'{s}')

    def logi(self, s, remote=False):
        if not remote:
            filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
            lineno = sys._getframe().f_back.f_lineno
            s = f'[{os.getpid()}] {filename}:{lineno} --> {s}'
        self.log_handler.send_message(MessageType.LOG, LogType.INFO, obj=f'{s}')

    def logw(self, s, remote=False):
        if not remote:
            filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
            lineno = sys._getframe().f_back.f_lineno
            s = f'[{os.getpid()}] {filename}:{lineno} --> {s}'
        self.log_handler.send_message(MessageType.LOG, LogType.WARNING, obj=f'{s}')

    def loge(self, s, remote=False):
        if not remote:
            filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
            lineno = sys._getframe().f_back.f_lineno
            s = f'[{os.getpid()}] {filename}:{lineno} --> {s}'
        self.log_handler.send_message(MessageType.LOG, LogType.ERROR, obj=f'{s}')

    def logc(self, s, remote=False):
        if not remote:
            filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
            lineno = sys._getframe().f_back.f_lineno
            s = f'[{os.getpid()}] {filename}:{lineno} --> {s}'
        self.log_handler.send_message(MessageType.LOG, LogType.CRITICAL, obj=f'{s}')


class JetRepApp(Application):
    """
    This is a repnet run on the jetson nano application.
    """
    name = Unicode('JetRepApp')
    description = Unicode(__doc__)

    svc_name_jetapi = Unicode('jetapi', read_only=True)
    svc_name_jetgst = Unicode('jetgst', read_only=True)
    svc_name_jetsrs = Unicode('jetsrs', read_only=True)
    tsk_name_engine = Unicode(TRTEngineProcess.name, read_only=True)
    tsk_name_prerep = Unicode(TRTPrerepProcess.name, read_only=True)
    tsk_name_postrep = Unicode(TRTPostrepProcess.name, read_only=True)

    config_file = Unicode('', help='Load this config file').tag(config=True)
    log_file = Unicode('/tmp/jetrep.log', help='Write log to file ').tag(config=True)

    rpc_ip = Unicode('127.0.0.1', help='Set zerorpc host').tag(config=True)
    rpc_port = Int(8181, help='Set zerorpc port').tag(config=True)

    classes = List([PSContext, SoftwareUpgrade])

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

    @traitlets.observe('log_level')
    def _log_level_changed(self, change):
        new = change.new
        if isinstance(new, str):
            new = getattr(logging, new)
            self.log_level = new
        self.log.setLevel(new)

    @traitlets.observe('log_datefmt', 'log_format')
    def _log_format_changed(self, change):
        _log_formatter = self._log_formatter_cls(fmt=self.log_format, datefmt=self.log_datefmt)
        for handler in self.log.handlers:
            handler.setFormatter(_log_formatter)

    @traitlets.default('log')
    def _log_default(self):
        log = logging.getLogger(self.__class__.__name__)
        log.setLevel(self.log_level)

        # def thread_id_filter(record):
        #     record.thread_id = threading.get_native_id() # >= py3.8
        #     return record

        formatter = self._log_formatter_cls(fmt=self.log_format, datefmt=self.log_datefmt)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        # console.addFilter(thread_id_filter)

        filelog = RotatingFileHandler(
                self.log_file, mode='a', maxBytes=5*1024*1024, backupCount=5, encoding=None, delay=0)
        filelog.setFormatter(formatter)

        log.addHandler(console)
        log.addHandler(filelog)
        return log

    def initialize(self, argv=None):
        self.parse_command_line(argv)
        if not os.path.exists(self.config_file):
            shutil.copyfile(DP.JETREP_DEF_CONF_PATH, self.config_file)
        if self.config_file:
            self.load_config_file(self.config_file)
        print(self.config)
        # print(self.print_help(classes=True))

    def setup(self):
        self.log_looper = LogHandlerThread()
        self.main_looper = MainHandlerThread()
        self.native = NativeHandler(self, LogHandler.instance(self))
        DefaultHandler.instance(self)
        NetworkHandler.instance(self)
        StateHandler.instance(self)
        NotifyHandler.instance(self)

        self.native.logi('Setup Rpc server')
        self.rpc_task = ServiceRPC(self, self.rpc_ip, self.rpc_port)

        self.native.logi('Setup Trt Tasks')
        self.app_exit, self.mq_in, self.mq_out = Event(), Queue(), Queue()
        self.tasks = {}
        for cls in (TRTEngineProcess, TRTPrerepProcess, TRTPostrepProcess):
            self.native.logi(f'Setup {cls.name}')
            self.tasks[cls.name] = cls(self.app_exit, ip=self.rpc_ip, port=self.rpc_port, mq_in=self.mq_in, mq_out=self.mq_out)
        self.psctx = PSContext(self.native, config=self.config)
        self.psctx.setup()
        self.softu = SoftwareUpgrade(self.native, config=self.config)
        self.softu.setup()

        self.event_monitor = SystemEventMonitor(self.native, self.app_exit)
        self.event_monitor.setup()

    def app_update_config(self, config_file):
        self.load_config_file(config_file)
        self.psctx.update_config(self.config)
        self.softu.update_config(self.config)
        self.native.logd(self.config)
        self.native.send_message(MessageType.NOTIFY, NotifyType.APP_CONF, PayloadType.CONFIG_UPDATE)

    def reset_config_file(self):
        shutil.copyfile(DP.JETREP_DEF_CONF_PATH, self.config_file)
        self.app_update_config(self.config_file)
        return True

    def meld_config_file(self, conf_dict):
        with open(self.config_file, 'r') as fr:
            MeldDict.meld_iters = False
            conf = json.load(fr)
            self.log.error(conf)
            meld_dict = MeldDict(conf) + conf_dict
            self.log.error(meld_dict)
        with open(self.config_file, 'w') as fw:
            fw.write(json.dumps(meld_dict, indent=4))
        self.app_update_config(self.config_file)
        return True

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def start(self):
        self.native.logi('Starting...')
        self.set_state(StateType.STARTING)
        self.log_looper.start()
        self.main_looper.start()
        self.rpc_task.start()
        self.event_monitor.start()
        self.native.send_message(MessageType.NOTIFY, NotifyType.APP_CONF, PayloadType.CONFIG_LOADED)
        self.native.send_message(MessageType.NOTIFY, NotifyType.TO_CLOUD, PayloadType.APP_VERSION)

    def restart(self):
        return not util_start_service('jetrep', restart=True)

    def stop(self):
        self.native.logi('Stopping...')
        self.set_state(StateType.STOPPING)
        self.app_exit.set()
        self.event_monitor.stop()
        self.native.send_message(MessageType.CTRL, CommandType.APP_STOP, ServiceType.RT_INFER_POSTREP)

    def wait(self, timeout=10):
        for _ in range(timeout):
            result = self.status()
            self.native.logi(f'Status: [{result}]')
            if not any(list(result.values())):
                break
            time.sleep(1)

    def status(self):
        result = {}
        result[self.svc_name_jetgst] = util_check_service(self.svc_name_jetgst)
        result[self.svc_name_jetsrs] = util_check_service(self.svc_name_jetsrs)
        result[self.svc_name_jetapi] = util_check_service(self.svc_name_jetapi)
        for name, tsk in self.tasks.items():
            result[name] = tsk.is_alive()
        return result

    def start_trt_postrep(self):
        self.native.logi('Start Trt PostRep')
        self.tasks[self.tsk_name_postrep].start()
        return True

    def stop_trt_postrep(self):
        self.native.logi('Stop Trt PostRep')
        self.tasks[self.tsk_name_postrep].stop(self.native)
        return True

    def start_trt_prerep(self):
        self.native.logi('Start Trt PreRep')
        self.tasks[self.tsk_name_prerep].start()
        return True

    def stop_trt_prerep(self):
        self.native.logi('Stop Trt PreRep')
        self.tasks[self.tsk_name_prerep].stop(self.native)
        return True

    def start_trt_engine(self):
        self.native.logi('Start Trt Engine')
        self.tasks[self.tsk_name_engine].start()
        return True

    def stop_trt_engine(self):
        self.native.logi('Stop Trt Engine')
        self.tasks[self.tsk_name_engine].stop(self.native)
        return True

    def start_gst_launch(self):
        self.native.logi('Start Gst Launch')
        if util_check_service(self.svc_name_jetgst):
            util_stop_service(self.svc_name_jetgst)
        return not util_start_service(self.svc_name_jetgst)

    def stop_gst_launch(self):
        self.native.logi('Stop Gst Launch')
        return not util_stop_service(self.svc_name_jetgst) \
                if util_check_service(self.svc_name_jetgst) else True

    def start_srs_webrtc(self):
        self.native.logi('Start Srs Webrtc')
        return not util_start_service(self.svc_name_jetsrs, True)

    def stop_srs_webrtc(self):
        self.native.logi('Stop Srs Webrtc')
        return not util_stop_service(self.svc_name_jetsrs) \
                if util_check_service(self.svc_name_jetsrs) else True

    def start_api_handler(self):
        self.native.logi('Start Api Handler')
        return not util_start_service(self.svc_name_jetapi, True)

    def stop_api_handler(self):
        self.native.logi('Stop Api Handler')
        return not util_stop_service(self.svc_name_jetapi) \
                if util_check_service(self.svc_name_jetapi) else True

    def start_network(self):
        pass

    def run(self, argv=None):
        try:
            self.initialize(argv)
            self.setup()
            self.start()
            self.event_monitor.loop()
        except KeyboardInterrupt:
            self.native.logw('JetRep Quit!')
        except Exception:
            self.native.loge(traceback.format_exc(limit=6))
        finally:
            self.stop()
            self.wait(timeout=25)
            self.rpc_task.stop()
            self.rpc_task.join()
            self.native.logw('JetRepApp End!!!!')
            os._exit(os.EX_OK)


# def signal_handler(sig, frame):
#     app.log.info('JetRepApp handle signal: [%d]' % sig)
#     app.stop()
#     app.wait(timeout=25)
#     time.sleep(1)
#     os._exit(os.EX_OK)
# 
# 
# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    app = JetRepApp()
    app.run()
