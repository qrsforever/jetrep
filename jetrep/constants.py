#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file constants.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-17 18:51

import os


class JPath(object):
    WORKING_DIRECTORY = '.'
    JETREP_CONF_PATH = os.path.join(WORKING_DIRECTORY, 'runtime', 'jetrep.json')
