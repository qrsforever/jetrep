#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file state.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:51

from jetrep.core.message import MessageHandler
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType
)


class StateHandler(MessageHandler):
    def __init__(self, app):
        super(StateHandler, self).__init__(app, keys=[MessageType.STATE])

    def on_service_srs(self, state, obj):
        if state == StateType.STARTING:
            return True
        if state == StateType.STARTED:
            return self.app.start_gst_launch()
        return False

    def on_service_gst(self, state, obj):
        if state == StateType.STARTED:
            return self.app.start_trt_engine()
        return False

    def on_service_api(self, state, obj):
        if state == StateType.STARTING:
            return self.app.start_srs_webrtc()
        return False

    def on_task_engine(self, state, obj):
        if state == StateType.STARTED:
            return self.app.start_trt_prerep()
        return False

    def on_task_prerep(self, state, obj):
        if state == StateType.STARTED:
            return self.app.start_trt_postrep()
        return False

    def handle_message(self, what, arg1, arg2, obj):
        self.log.debug(f'{what} {arg1} {arg2} {obj}')
        if what != MessageType.STATE:
            return False
        if arg1 == ServiceType.SRS:
            return self.on_service_srs(arg2, obj)
        if arg1 == ServiceType.GST:
            return self.on_service_gst(arg2, obj)
        if arg1 == ServiceType.API:
            return self.on_service_api(arg2, obj)
        if arg1 == ServiceType.RT_INFER_ENGINE:
            return self.on_task_engine(arg2, obj)
        if arg1 == ServiceType.RT_INFER_PREREP:
            return self.on_task_prerep(arg2, obj)
        return False

    @staticmethod
    def instance(app):
        return StateHandler(app)


if __name__ == "__main__":
    import time
    from jetrep.core.message import MainHandlerThread
    handler = StateHandler()
    main = MainHandlerThread()
    main.start()
    time.sleep(1)
    handler.send_message(MessageType.STATE, arg1=1, obj=[1,2,3,4])
    time.sleep(3)
    handler.send_message(MessageType.QUIT)
    main.join()
    print("end")
