#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file constants.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-17 18:51

import os
import os.path as osp


class DefaultPath(object):
    WORKING_DIRECTORY = os.getcwd()
    RUNTIME_DIRECTORY = osp.join(WORKING_DIRECTORY, 'runtime')
    JETREP_DEF_CONF_PATH = osp.join(WORKING_DIRECTORY, 'etc', 'jetrep.json')
    JETREP_CONF_PATH = osp.join(RUNTIME_DIRECTORY, 'jetrep.json')

    VIDEO_CLIPS_PATH = osp.join(RUNTIME_DIRECTORY, 'videos')


class DefaultServer(object):
    RTMP_SERVER = '0.0.0.0'
    RTMP_PORT = 1935
    RTMP_STREAM_PRE = 1
    RTMP_STREAM_POST = 2
    RTMP_DVR_DURATION = 900
