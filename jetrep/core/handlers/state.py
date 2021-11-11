#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file state.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:51

from jetrep.core.message import MessageHandler
from jetrep.core.message import MessageType


class StateHandler(MessageHandler):
    def __init__(self, app):
        super(StateHandler, self).__init__(app, keys=[MessageType.STATE])

    def handle_message(self, what, arg1, arg2, obj):
        if what != MessageType.STATE:
            return False
        self.app.log.info(f'{what}, {arg1}, {arg2}')
        return True

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
