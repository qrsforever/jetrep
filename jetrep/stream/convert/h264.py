#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file h264.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:52


from traitlets import Unicode, Int, Enum
from .gconvert import GDataConvert


class GH264CodecCvt(GDataConvert):
    name = Unicode(default_value='h264cvt')
    bitrate = Int(default_value=40000, help='Set bitrate for v4l2 encode').tag(config=True)
    profile = Enum((0,2,4), default_value=0, help='Set profile for v4l2 encode').tag(config=True)
    preset_level = Enum((0,1,2,3,4), default_value=1, help='HW preset level for encode').tag(config=True)

    def gst_pipe(self):
        return [
            'nvvidconv',
            f'nvv4l2h264enc bitrate={self.bitrate} maxperf-enable=1 profile={self.profile} preset-level={self.preset_level} iframeinterval=500',
            'h264parse',
        ] + super().gst_pipe()
