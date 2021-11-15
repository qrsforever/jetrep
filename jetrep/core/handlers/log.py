#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file log.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 20:31

from multiprocessing import Queue
from jetrep.core.message import MessageHandler
from jetrep.core.message import MessageType
from jetrep.core.message import LogType


class NullLogger(object):
    def __getattr__(self, method):
        return print


class LogHandler(MessageHandler):
    mq = Queue()
    handlers = {}

    def __init__(self, app):
        super(LogHandler, self).__init__(app, keys=[MessageType.LOG])
        if app is not None:
            self.logger = app.log
        else:
            self.logger = NullLogger()

    def handle_message(self, what, arg1, arg2, obj):
        if what != MessageType.LOG:
            return False
        if arg1 == LogType.DEBUG:
            self.logger.debug(f'{obj}')
        elif arg1 == LogType.INFO:
            self.logger.info(f'{obj}')
        elif arg1 == LogType.WARN:
            self.logger.warn(f'{obj}')
        elif arg1 == LogType.ERROR:
            self.logger.error(f'{obj}')
        return True

    @staticmethod
    def instance(logger):
        return LogHandler(logger)


if __name__ == "__main__":
    import time
    from jetrep.core.message import MainHandlerThread
    handler = LogHandler()
    main = MainHandlerThread()
    main.start()
    time.sleep(1)
    handler.send_message(MessageType.LOG, arg1=LogType.WARN, obj=[1,2,3,4])
    time.sleep(3)
    handler.send_message(MessageType.QUIT)
    main.join()
    print("end")
