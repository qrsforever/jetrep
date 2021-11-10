#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file rtmp.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:55

from traitlets import Unicode, Int
from .gsink import GDataSink


class SRSRtmpSink(GDataSink):
    name = Unicode(default_value='rtmpsink')
    server = Unicode(default_value='0.0.0.0', help='RTMP server address').tag(config=True)
    port = Int(default_value=1935, help='RTMP server port').tag(config=True)
    stream = Unicode(allow_none=False, help='RTMP server stream').tag(config=True)
    max_lateness = Int(default_value=3, help='Maximum number of seconds that a buffer can be late before it is dropped').tag(config=True)

    def gst_pipe(self):
        return [
            'flvmux',
            f'rtmpsink max-lateness={self.max_lateness * 1000000000} location=rtmp://{self.server}:{self.port}/live/{self.stream}',
        ]
