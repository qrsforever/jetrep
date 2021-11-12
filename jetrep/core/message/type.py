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


@unique
class LogType(IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4


@unique
class ServiceType(IntEnum):
    SRS = 1
    GST = 2
    API = 3

    RT_INFER_ENGINE = 4


@unique
class StateType(IntEnum):
    NOP = 1
    STARTING = 2
    STARTED = 3
    STOPPING = 4
    STOPPED = 5


if __name__ == "__main__":
    print(MessageType.LOG, type(MessageType.LOG))
    for t in MessageType:
        print(t)
    for t in MessageType.__members__.items():
        print(t)
