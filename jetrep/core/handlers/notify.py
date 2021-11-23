#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file notify.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-19 21:38


from jetrep.core.message import MessageHandler
from jetrep.core.message import (
     MessageType,
     NotifyType,
     PayloadType,
)
from jetrep.constants import APP_VERSION_INFO


class NotifyHandler(MessageHandler):
    def __init__(self, app):
        super(NotifyHandler, self).__init__(app, keys=[MessageType.NOTIFY, MessageType.TIMER])

    def on_cloud_event(self, arg2, obj):
        if arg2 == PayloadType.APP_VERSION_INFO:
            self.app.log.warning(f'Not impl: {APP_VERSION_INFO}')
            return True
        elif arg2 == PayloadType.REP_INFER_RESULT:
            self.app.log.warning(f'Not impl: {obj}')
            return True
        return False

    def on_usb_event(self, arg2, obj):
        if arg2 == 1:
            pass
        return False

    def handle_message(self, what, arg1, arg2, obj):
        if what == MessageType.NOTIFY:
            if arg1 == NotifyType.TO_CLOUD:
                return self.on_cloud_event(arg2, obj)
            if arg1 == NotifyType.USB_MOUNT:
                return self.on_cloud_event(arg2, obj)
            return False

        if what == MessageType.TIMER:
            return False

        return False

    @staticmethod
    def instance(app):
        return NotifyHandler(app)
