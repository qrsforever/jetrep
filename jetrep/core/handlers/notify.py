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


class NotifyHandler(MessageHandler):
    def __init__(self, app):
        super(NotifyHandler, self).__init__(app, keys=[MessageType.NOTIFY, MessageType.QUIT])

    def on_cloud_event(self, arg2, obj):
        if arg2 == PayloadType.REP_INFER_RESULT:
            # TODO
            self.app.log.warning(f'Not impl: {obj}')
            return True
        return False

    def handle_message(self, what, arg1, arg2, obj):
        if arg1 == NotifyType.TO_CLOUD:
            return self.on_cloud_event(arg2, obj)
        return False

    @staticmethod
    def instance(app):
        return NotifyHandler(app)
