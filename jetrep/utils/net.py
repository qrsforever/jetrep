#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file net.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 15:12

import socket
import time
import uuid


def util_check_port(port, ip='127.0.0.1', trycnt=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(trycnt):
        code = sock.connect_ex((ip, port))
        if code == 0:
            return True
        time.sleep(1)
    return False


def util_get_lanip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        val = '0.0.0.0'
        s.connect(('8.8.8.8', 80))
        val = s.getsockname()[0]
    finally:
        s.close()
    return val


def util_get_uuid():
    return uuid.UUID(int=uuid.getnode()).hex[-12:]
