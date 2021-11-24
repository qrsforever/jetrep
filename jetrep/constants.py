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
    APP_NAME = os.path.basename(WORKING_DIRECTORY)
    APP_LINK = f'/{APP_NAME}'
    RUNTIME_NAME = 'runtime'
    APP_VERSION_PATH = osp.join(WORKING_DIRECTORY, 'version.txt')
    RUNTIME_DIRECTORY = osp.join(WORKING_DIRECTORY, RUNTIME_NAME)
    CRONTAB_DIRECTORY = osp.join(WORKING_DIRECTORY, 'etc', 'crontab')
    JETREP_DEF_CONF_PATH = osp.join(WORKING_DIRECTORY, 'etc', 'jetrep.json')
    JETREP_CONF_PATH = osp.join(RUNTIME_DIRECTORY, 'jetrep.json')

    CONFIG_VALID_NOD = osp.join(RUNTIME_DIRECTORY, 'SUCCESS') # TODO Don't modify used in scripts

    VIDEO_CLIPS_PATH = osp.join(RUNTIME_DIRECTORY, 'videos')

    UPDATE_CONFIG_PATH = osp.join(RUNTIME_DIRECTORY, 'jetrep_update.json')
    UPDATE_ZIP_PATH = osp.join(RUNTIME_DIRECTORY, 'jetrep_update.zip')
    UPDATE_INSTALL_PATH = '/var/jetrep/archives' # TODO Don't modify used in scripts


class DefaultServer(object):
    RTMP_SERVER = '0.0.0.0'
    RTMP_PORT = 1935
    RTMP_STREAM_PRE = 1
    RTMP_STREAM_POST = 2
    RTMP_DVR_DURATION = 900
