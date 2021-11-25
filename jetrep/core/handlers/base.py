#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file default.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:59


import time
from jetrep.core.message import MessageHandler
from jetrep.core.message import (
    MessageType,
    CommandType,
    ServiceType,
)


class DefaultHandler(MessageHandler):
    def __init__(self, app):
        super(DefaultHandler, self).__init__(app, keys=[MessageType.CTRL, MessageType.QUIT])

    def on_ctrl_start(self, arg2, obj):
        if arg2 == ServiceType.API:
            return self.app.start_api_handler()
        if arg2 == ServiceType.SRS:
            return self.app.start_srs_webrtc()
        if arg2 == ServiceType.GST:
            return self.app.start_gst_launch()
        if arg2 == ServiceType.RT_INFER_ENGINE:
            return self.app.start_trt_engine()
        if arg2 == ServiceType.RT_INFER_PREREP:
            return self.app.start_trt_prerep()
        if arg2 == ServiceType.RT_INFER_POSTREP:
            return self.app.start_trt_postrep()
        return False

    def on_ctrl_stop(self, arg2, obj):
        if arg2 == ServiceType.API:
            return self.app.stop_api_handler()
        if arg2 == ServiceType.SRS:
            return self.app.stop_srs_webrtc()
        if arg2 == ServiceType.GST:
            return self.app.stop_gst_launch()
        if arg2 == ServiceType.RT_INFER_ENGINE:
            return self.app.stop_trt_engine()
        if arg2 == ServiceType.RT_INFER_PREREP:
            return self.app.stop_trt_prerep()
        if arg2 == ServiceType.RT_INFER_POSTREP:
            return self.app.stop_trt_postrep()
        return False

    def handle_message(self, what, arg1, arg2, obj):
        if what == MessageType.CTRL:
            if arg1 == CommandType.APP_START:
                return self.on_ctrl_start(arg2, obj)
            if arg1 == CommandType.APP_STOP:
                return self.on_ctrl_stop(arg2, obj)
            if arg1 == CommandType.APP_RESTART:
                return self.app.restart()
            if arg1 == CommandType.API_SET_PARAM:
                return self.app.meld_config_file(obj)
            if arg1 == CommandType.API_RESET_PARAM:
                return self.app.reset_config_file()
        return False

    @staticmethod
    def instance(app):
        return DefaultHandler(app)


if __name__ == "__main__":
    from jetrep.core.message import MainHandlerThread
    handler = DefaultHandler()
    main = MainHandlerThread()
    main.start()
    time.sleep(1)
    handler.send_message(MessageType.CTRL, arg1=1, obj=[1,2,3,4])
    time.sleep(3)
    handler.send_message(MessageType.QUIT)
    main.join()
    print("end")
