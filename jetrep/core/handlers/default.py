#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file default.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:59


from jetrep.core.message import MessageHandler
from jetrep.core.message import (
    MessageType,
    CommandType,
)


class DefaultHandler(MessageHandler):
    def __init__(self, app):
        super(DefaultHandler, self).__init__(app, keys=[MessageType.CTRL, MessageType.QUIT])

    def handle_message(self, what, arg1, arg2, obj):
        self.log.info(f'{what} {arg1} {arg2} {obj}')
        if what == MessageType.CTRL:
            if arg1 == CommandType.APP_START:
                return self.app.start_api_handler()
            if arg1 == CommandType.APP_STOP:
                return self.app.stop_gst_launch()
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
