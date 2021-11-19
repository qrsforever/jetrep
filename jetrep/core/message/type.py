#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file type.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 19:40


from enum import IntEnum, unique


@unique
class MessageType(IntEnum):
    LOG = 1
    CTRL = 2
    STATE = 3
    QUIT = 99


@unique
class CommandType(IntEnum):
    NOP = 1
    APP_START = 2
    APP_STOP = 3
    APP_RESTART = 4

    API_SET_PARAM = 10


@unique
class LogType(IntEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


@unique
class ServiceType(IntEnum):
    SRS = 1
    GST = 2
    API = 3

    RT_INFER_ENGINE = 4
    RT_INFER_PREREP = 5
    RT_INFER_POSTREP = 6

    ALL = 99


@unique
class StateType(IntEnum):
    NOP = 1
    STARTING = 2
    STARTED = 3
    STOPPING = 4
    STOPPED = 5
    STOPPTIMEOUT = 6
    RUNNING = 7

    CRASHED = 99


@unique
class EmptyType(IntEnum):
    NOP = 1


def pretty_format(what, arg1, arg2):
    if arg2 < 0:
        arg2 = EmptyType(1)
    if not isinstance(what, IntEnum):
        if what == MessageType.LOG:
            arg1 = LogType(arg1)
        elif what == MessageType.CTRL:
            arg1 = CommandType(arg1)
        elif what == MessageType.STATE:
            arg1 = ServiceType(arg1)
            arg2 = StateType(arg2)
        else:
            return '%d, %d, %d' % (what, arg1, arg2)
        what = MessageType(what)
    return '%s, %s, %s' % (what, arg1, arg2)
        

if __name__ == "__main__":
    print(MessageType.LOG, type(MessageType.LOG))
    for t in MessageType:
        print(t)
    for t in MessageType.__members__.items():
        print(t)
