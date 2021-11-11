#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file default.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:59


from jetrep.core.message import MessageHandler
from jetrep.core.message import MessageType


class DefaultHandler(MessageHandler):
    def __init__(self, app):
        super(DefaultHandler, self).__init__(keys=[MessageType.CTRL, MessageType.QUIT])
        self.app = app

    def handle_message(self, what, arg1, arg2, obj):
        if what == MessageType.CTRL:
            return True
        
        return False

    @staticmethod
    def instance(app):
        return DefaultHandler(app)


if __name__ == "__main__":
    import time
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
