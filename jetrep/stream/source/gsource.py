#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file gsource.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:41

import traitlets
import uuid
from traitlets import Unicode, Int, Enum
from jetrep.stream.gelement import GElement


class GDataSource(GElement):
    uuid = Unicode('')

    width = Int(default_value=640, help='Source video frame width').tag(config=True)
    height = Int(default_value=480, help='Source video frame height').tag(config=True)
    framerate = Int(default_value=30, help='Source video frame rate').tag(config=True)
    number_buffers = Int(default_value=-1, help='Number buffers of source video frames').tag(config=True)
    flip_method = Enum((0,1,2,3,4,5,6,7), default_value=0, help='Set the video flip methods').tag(config=True)

    def __init__(self, *args, **kwargs):
        super(GDataSource, self).__init__(None, *args, **kwargs)

    @traitlets.default('uuid')
    def _default_uuid(self):
        return uuid.UUID(int=uuid.getnode()).hex[-12:]

    def gst_pipe(self):
        return [
            f'nvvidconv flip-method={self.flip_method}',
            f'video/x-raw,width={self.width},height={self.height},format=BGRx',
            f'textoverlay halignment=0 valignment=2 text={self.uuid}',
            f'clockoverlay halignment=2 time-format="%Y/%m/%d %H:%M:%S"',
            f'tee name=t_{self.name}'
        ]
