#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file shm.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:55

import os
import traitlets
from traitlets import Unicode, Int
from .gsink import GDataSink


class ShareMemorySink(GDataSink):
    name = Unicode(default_value='shmsink')
    path = Unicode(default_value='', allow_none=False, help='The path to the control socket(shared memory).').tag(config=True)
    size = Int(default_value=10000000, min=0, max=4294967295, help='Size of the shared memory area').tag(config=True)

    @traitlets.validate('path')
    def _check_socket_path(self, proposal):
        path = proposal['value']
        if not os.access(os.path.dirname(path), os.X_OK):
            raise RuntimeError(f'Cannot operate {path} permission!')
        if os.path.exists(path):
            os.unlink(path)
        return path

    def gst_pipe(self):
        return [
            f'videoconvert',
            f'video/x-raw, format=(string)BGR',
            f'shmsink socket-path="{self.path}" shm-size={self.size} sync=true wait-for-connection=false'
        ]
