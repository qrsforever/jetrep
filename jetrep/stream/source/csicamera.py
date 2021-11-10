#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file csicamera.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:47

from traitlets import Unicode, Int, Enum
from .gsource import GDataSource


class CSICamera(GDataSource):
    name = Unicode(default_value='csicam')
    device = Int(default_value=0)
    flip_method = Enum((0,1,2,3,4,5,6,7), default_value=6, help='Set the video flip methods').tag(config=True)

    def gst_pipe(self):
        return [
            f'nvarguscamerasrc name={self.name} sensor-id={self.device} num-buffers={self.number_buffers}',
            f'video/x-raw(memory:NVMM),width={self.width},height={self.height},format=NV12,framerate={self.framerate}/1',
        ] + super().gst_pipe()
