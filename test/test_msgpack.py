#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import msgpack


class FBucket(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    tmp_dir = '/tmp'

    def __init__(self):
        self.token = int(time.time() * 1000)
        self.raw_frames_count = 0
        self.raw_frames_path = f'{self.tmp_dir}/{self.token}.mp4'
        self.inputs = []
        self.selected_indices = []


f = FBucket()
f.aaa = 1000

ff = msgpack.unpackb(msgpack.packb(f))
ff
