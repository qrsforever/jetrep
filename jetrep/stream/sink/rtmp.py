#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file rtmp.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:55

import traitlets
from traitlets import Unicode, Int, Enum
from .gsink import GDataSink


class SRSRtmpSink(GDataSink):
    name = Unicode(default_value='rtmpsink')
    server = Unicode(default_value='0.0.0.0', help='RTMP server address').tag(config=True)
    port = Int(default_value=1935, help='RTMP server port').tag(config=True)
    stream = Unicode(default_value='', help='RTMP server stream').tag(config=True)
    duration = Enum((60, 300, 600, 900, 1200, 1800), default_value=900).tag(config=True)
    max_lateness = Int(default_value=3, help='Maximum number of seconds that a buffer can be late before it is dropped').tag(config=True)

    @traitlets.default('stream')
    def _default_stream(self):
        return self.uuid

    def gst_pipe(self):
        max_lateness = self.max_lateness * 1000000000
        location = f'rtmp://{self.server}:{self.port}/pre/{self.stream}?vhost=jet{self.duration}'
        return [
            'flvmux',
            f'rtmpsink max-lateness={max_lateness} location={location}',
        ]
