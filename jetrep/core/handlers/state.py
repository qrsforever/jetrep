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
    CommandType,
    ServiceType,
    StateType
)


class StateHandler(MessageHandler):
    def __init__(self, app):
        super(StateHandler, self).__init__(app, keys=[MessageType.STATE])

    def on_booting_message(self, what, arg1, arg2, obj):
        if arg2 == StateType.CRASHED:
            return self.send_message(MessageType.CTRL, CommandType.APP_RESTART)

        if arg1 == ServiceType.API:
            if arg2 == StateType.STARTED:
                return self.send_message(MessageType.CTRL, CommandType.APP_START, ServiceType.SRS)
        if arg1 == ServiceType.SRS:
            if arg2 == StateType.STARTED:
                return self.send_message(MessageType.CTRL, CommandType.APP_START, ServiceType.GST)
        if arg1 == ServiceType.GST:
            if arg2 == StateType.STARTED:
                return self.send_message(MessageType.CTRL, CommandType.APP_START, ServiceType.RT_INFER_ENGINE)
        if arg1 == ServiceType.RT_INFER_ENGINE:
            if arg2 == StateType.STARTED:
                return self.send_message(MessageType.CTRL, CommandType.APP_START, ServiceType.RT_INFER_PREREP)
        if arg1 == ServiceType.RT_INFER_PREREP:
            if arg2 == StateType.STARTED:
                return self.send_message(MessageType.CTRL, CommandType.APP_START, ServiceType.RT_INFER_POSTREP)
        if arg1 == ServiceType.RT_INFER_POSTREP:
            if arg2 == StateType.STARTED: # all process create ok!
                return self.app.set_state(StateType.RUNNING)
        return False

    def on_shutdown_message(self, what, arg1, arg2, obj):
        if arg2 in (StateType.STOPPED, StateType.STOPPTIMEOUT, StateType.CRASHED):
            if arg1 == ServiceType.RT_INFER_POSTREP:
                return self.send_message(MessageType.CTRL, CommandType.APP_STOP, ServiceType.RT_INFER_PREREP)
            if arg1 == ServiceType.RT_INFER_PREREP:
                return self.send_message(MessageType.CTRL, CommandType.APP_STOP, ServiceType.RT_INFER_ENGINE)

            status = self.app.status()
            if arg1 == ServiceType.RT_INFER_ENGINE:
                if status[self.app.svc_name_jetgst]:
                    return self.send_message(MessageType.CTRL, CommandType.APP_STOP, ServiceType.GST)
                arg1 = ServiceType.GST

            if arg1 == ServiceType.GST:
                if status[self.app.svc_name_jetsrs]:
                    return self.send_message(MessageType.CTRL, CommandType.APP_STOP, ServiceType.SRS)
                arg1 = ServiceType.SRS

            if arg1 == ServiceType.SRS:
                if status[self.app.svc_name_jetapi]:
                    return self.send_message(MessageType.CTRL, CommandType.APP_STOP, ServiceType.API)
        return False

    def on_running_message(self, what, arg1, arg2, obj):
        if arg2 == StateType.CRASHED:
            return self.send_message(MessageType.CTRL, CommandType.APP_RESTART)
        return False

    def handle_message(self, what, arg1, arg2, obj):
        if what != MessageType.STATE:
            return False
        if self.app.get_state() == StateType.STARTING:
            self.on_booting_message(what, arg1, arg2, obj)
        elif self.app.get_state() == StateType.STOPPING:
            self.on_shutdown_message(what, arg1, arg2, obj)
        elif self.app.get_state() == StateType.RUNNING:
            self.on_running_message(what, arg1, arg2, obj)

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
