#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file usbcamera.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:45


from traitlets import Unicode, Int
from .gsource import GDataSource


class USBCamera(GDataSource):
    name = Unicode(default_value='usbcam')
    device = Int(default_value=1)

    def gst_pipe(self):
        # io-mode = 2 (mmap)
        return [
            f'v4l2src name={self.name} device=/dev/video{self.device} io-mode=2 num-buffers={self.number_buffers}',
            f'image/jpeg,width={self.width},height={self.height},framerate={self.framerate}/1,format=MJPG',
            'nvjpegdec',
            'video/x-raw',
            'nvvidconv',
            f'video/x-raw(memory:NVMM),width={self.width},height={self.height},format=NV12,framerate={self.framerate}/1',
        ] + super().gst_pipe()
