#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file base.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 18:50

import abc
from multiprocessing import Queue
from .type import pretty_format


class Message(object):
    def __init__(self, what, arg1, arg2, obj, callback):
        self.what = what
        self.arg1 = arg1
        self.arg2 = arg2
        self.obj = obj
        self.callback = callback # TODO

    def __str__(self):
        obj = self.obj[:32] if isinstance(self.obj, str) else self.obj.__class__.__name__
        return f'msg: ({pretty_format(self.what, self.arg1, self.arg2)}, {obj})'

    @staticmethod
    def obtain(what, arg1, arg2, obj, cb=None):
        return Message(what, arg1, arg2, obj, cb)


class MessageHandler(metaclass=abc.ABCMeta):
    mq = Queue()
    handlers = {}

    def __init__(self, app, keys=[]):
        for ty in keys:
            if ty not in self.handlers:
                self.handlers[ty] = []
            self.handlers[ty].append(self)
        self.app = app
        self.log = app.log

    @abc.abstractmethod
    def handle_message(self, what, arg1, arg2, obj):
        pass

    def send_message(self, what, arg1=-1, arg2=-1, obj=None, cb=None):
        msg = Message.obtain(what, arg1, arg2, obj, cb)
        self.mq.put(msg)
        return True

    def dispatch_message(self, msg):
        if msg.what != 1: # LOG
            self.log.info(msg)
        try:
            if msg.callback:
                return msg.callback.handle_message(msg.what, msg.arg1, msg.arg2, msg.obj)
            return self.handle_message(msg.what, msg.arg1, msg.arg2, msg.obj)
        except Exception as err:
            self.log.info(f'{err}')


if __name__ == "__main__":
    print(Message.obtain(1, 1, 1, [1,1,1]))
