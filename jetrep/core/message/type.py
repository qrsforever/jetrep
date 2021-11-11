#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file type.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-11 19:40


from enum import Enum, unique


@unique
class MessageType(Enum):
    LOG = 1
    CTRL = 2
    STATE = 3
    QUIT = 99


@unique
class LogType(Enum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4


@unique
class ServiceType(Enum):
    SRS = 1
    GST = 2
    API = 3


@unique
class StateType(Enum):
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
