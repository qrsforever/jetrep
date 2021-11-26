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
    NOP = -1
    LOG = 1
    CTRL = 2
    STATE = 3
    NOTIFY = 4
    TIMER = 5
    UPGRADE = 6
    NETWORK = 7
    QUIT = 99


@unique
class CommandType(IntEnum):
    NOP = -1
    APP_START = 1
    APP_STOP = 2
    APP_RESTART = 3
    API_SET_PARAM = 10
    API_RESET_PARAM = 11


@unique
class LogType(IntEnum):
    NOP = -1
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


@unique
class ServiceType(IntEnum):
    NOP = -1
    APP = 1
    SRS = 2
    GST = 3
    API = 4

    RT_INFER_ENGINE = 11
    RT_INFER_PREREP = 12
    RT_INFER_POSTREP = 13

    ALL = 99


@unique
class StateType(IntEnum):
    NOP = -1
    RUNNING = 1
    STARTING = 2
    STARTED = 3
    STOPPING = 4
    STOPPED = 5
    STOPPTIMEOUT = 6

    CRASHED = 99


@unique
class NotifyType(IntEnum):
    NOP = -1
    APP_CONF = 1
    TO_CLOUD = 2
    USB_MOUNT = 3


@unique
class TimerType(IntEnum):
    NOP = -1
    CHECK_UPDATE = 1


@unique
class UpgradeType(IntEnum):
    NOP = -1
    DEV = 1
    OTA = 2
    UDISK = 3


@unique
class NetworkType(IntEnum):
    NOP = -1
    CONNECTED = 1
    DISCONNECTED = 2
    ADD = 3
    REMOVE = 4
    UP = 5
    DOWN = 6

    WIFI_CONNECT = 11


@unique
class PayloadType(IntEnum):
    NOP = -1
    APP_VERSION = 1
    UPGRADE_SUCCESS = 2
    UPGRADE_ERROR = 3
    CONFIG_UPDATE = 4
    CONFIG_VALID = 5
    CONFIG_LOADED = 6
    UNKOWN7 = 7
    UNKOWN8 = 8
    UNKOWN9 = 9
    REP_INFER_RESULT = 10
    UNKOWN11 = 11
    UNKOWN12 = 12
    UNKOWN13 = 13
    UNKOWN14 = 14
    UNKOWN15 = 15
    UNKOWN16 = 16
    UNKOWN17 = 17
    UNKOWN18 = 18
    UNKOWN19 = 19
    UNKOWN20 = 20
    MOUNTED = 21
    UNMOUNTED = 22


def pretty_format(what, arg1, arg2):
    if not isinstance(what, IntEnum):
        if what == MessageType.LOG:
            arg1 = LogType(arg1)
        elif what == MessageType.CTRL:
            arg1 = CommandType(arg1)
        elif what == MessageType.STATE:
            arg1 = ServiceType(arg1)
            arg2 = StateType(arg2)
        elif what == MessageType.NOTIFY:
            arg1 = NotifyType(arg1)
        elif what == MessageType.TIMER:
            arg1 = TimerType(arg1)
        elif what == MessageType.UPGRADE:
            arg1 = UpgradeType(arg1)
        elif what == MessageType.NETWORK:
            arg1 = NetworkType(arg1)
        else:
            return '%d, %d, %d' % (what, arg1, arg2)
        if not isinstance(arg2, IntEnum):
            arg2 = PayloadType(arg2)
        what = MessageType(what)
    return '%s, %s, %s' % (what, arg1, arg2)


if __name__ == "__main__":
    print(MessageType.LOG, type(MessageType.LOG))
    for t in MessageType:
        print(t)
    for t in MessageType.__members__.items():
        print(t)
