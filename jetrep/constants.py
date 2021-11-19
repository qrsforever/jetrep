#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file constants.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-17 18:51

import os


class DefaultPath(object):
    WORKING_DIRECTORY = '.'
    JETREP_CONF_PATH = os.path.join(WORKING_DIRECTORY, 'runtime', 'jetrep.json')


class DefaultServer(object):
    RTMP_SERVER = '0.0.0.0'
    RTMP_PORT = 1935
    RTMP_STREAM_PRE = 1
    RTMP_STREAM_POST = 2
    RTMP_DVR_DURATION = 900
