#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file looper.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:07

import queue
import threading
from .base import MessageHandler as MH
from .type import MessageType


class MainHandlerThread(threading.Thread):
    def __init__(self):
        super(MainHandlerThread, self).__init__()

    def run(self):
        while True:
            try:
                msg = MH.mq.get(timeout=3)
                print(msg)
                if msg.what == MessageType.QUIT:
                    break
                if msg.what not in MH.handlers:
                    continue
                for handler in MH.handlers[msg.what]:
                    if handler.dispatch_message(msg):
                        break
            except queue.Empty:
                pass


if __name__ == "__main__":
    class TestHandler(MH):
        def __init__(self):
            super(TestHandler, self).__init__(keys=[MessageType.LOG])

        def handle_message(self, what, arg1, arg2, obj):
            print(what, arg1, arg2, obj)

    import time
    handler = TestHandler()
    main = MainHandlerThread()
    main.start()
    time.sleep(1)
    handler.send_message(MessageType.LOG)
    time.sleep(3)
    handler.send_message(MessageType.QUIT)
    main.join()
    print("end")
