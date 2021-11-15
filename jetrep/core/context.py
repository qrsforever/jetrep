#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file context.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-15 15:40

import os
import time
import jsonschema
import traitlets
from traitlets.config.configurable import Configurable
from traitlets import Bool, Int, Float, Unicode, Tuple, List, Dict, Enum # noqa


class PSContext(Configurable):
    frame_size = Tuple((640, 480))
    frame_rate = Int(30)
    focus_box = List(Float(min=0., max=1.), [0.0, 0.0, 1.0, 1.0], minlen=4, maxlen=4).tag(config=True)
    black_box = List(Float(min=0., max=1.), [0.0, 0.0, 0.0, 0.0], minlen=4, maxlen=4).tag(config=True)
    area_rate = Float(default_value=0.002, min=0.0, max=0.05).tag(config=True)
    strides = List(trait=Int(), default_value=[4], minlen=1, maxlen=3).tag(config=True)
    snip_root = Unicode('/tmp').tag(config=True)

    # synth_video_rtmp = Dict(traits={'server': Unicode(), 'port': Int(1935), 'stream': Unicode()})
    synth_video_schema = {
         'type' : 'object',
         'properties' : {
             'rtmp': {
                 'type': 'object',
                 'properties': {
                     'server' : {'type' : 'string'},
                     'port': {'type': 'number'},
                     'stream' : {'type' : 'string'},
                 },
                 'required': ['server', 'port', 'stream']
             },
             'file': {
                 'type': 'object',
                 'properties': {
                     'path': {'type': 'string'},
                 },
                 'required': ['path']
             }
         }
    }
    synth_video = Dict().tag(config=True)

    F = 64
    K = F * 15

    def __init__(self, *args, **kwargs):
        super(PSContext, self).__init__(*args, **kwargs)

        self._focus_box = None
        self._black_box = None
        self._stride = 4
        self._max_raw_frames = self._stride * self.K
        self._area_thresh = 0

    class FBucket(object):
        tmp_dir = '/tmp'

        def __init__(self):
            self.token = int(time.time() * 1000)
            self.raw_frames_count = 0
            self.raw_frames_path = f'{self.tmp_dir}/{self.token}.mp4'
            self.inputs = []
            self.selected_indices = []

        def __str__(self):
            return 'token: {}, raw_frames_count: {}, raw_frames_path: {}, selected_indices: {}'.format(
                self.token,
                self.raw_frames_count,
                self.raw_frames_path,
                self.selected_indices
            )

    def make_bucket(self):
        bucket = self.FBucket()
        bucket.frame_size = self.frame_size
        bucket.frame_rate = self.frame_rate
        bucket.focus_box = self._focus_box
        bucket.black_box = self._black_box
        bucket.stride = self._stride
        bucket.area_thresh = self._area_thresh
        bucket.max_frame_count = self._stride * self.K
        return bucket

    @staticmethod
    def calc_rect_box(w, h, box):
        return [int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])]

    @traitlets.observe('frame_size')
    def _on_frame_size(self, change):
        if self._focus_box:
            self._focus_box = self.calc_rect_box(change['new'][0], change['new'][1], self.focus_box)
        if self._black_box:
            self._black_box = self.calc_rect_box(change['new'][0], change['new'][1], self.black_box)
        if self._focus_box:
            x1, y1, x2, y2 = self._focus_box
            self._area_thresh = int((x2 - x1) * (y2 - y1) * self.area_rate)
        else:
            self._area_thresh = int(change['new'][0] * change['new'][1] * self.area_rate)

    @traitlets.observe('focus_box')
    def _on_focus_box(self, change):
        if change['new'] == [0., 0., 1., 1.]:
            self._focus_box = None
            return
        self._focus_box = self.calc_rect_box(self.frame_size[0], self.frame_size[1], change['new'])

    @traitlets.observe('black_box')
    def _on_black_box(self, change):
        if change['new'] == [0., 0., 0., 0.] or change['new'] == [1., 1., 1., 1.]:
            self._black_box = None
            return
        self._black_box = self.calc_rect_box(self.frame_size[0], self.frame_size[1], change['new'])

    @traitlets.observe('area_rate')
    def _on_area_rate(self, change):
        if self._focus_box:
            x1, y1, x2, y2 = self._focus_box
            self._area_thresh = (x2 - x1) * (y2 - y1) * change['new']
            return
        self._area_thresh = int(self.frame_size[0] * self.frame_size[1] * change['new'])

    @traitlets.observe('strides')
    def _on_strides(self, change):
        # TODO only support one stride
        self._stride = change['new'][0]
        self._max_raw_frames = self._stride * self.K

    @traitlets.observe('snip_root')
    def _on_snip_root(self, change):
        if os.path.isdir(change['new']):
            self.FBucket.tmp_dir = change['new']

    @traitlets.validate('focus_box')
    def _check_focus_box(self, proposal):
        value = proposal['value']
        if value[0] >= value[2] or value[1] >= value[3]:
            raise traitlets.TraitError(f'focus_box invalid: {value}')
        return value

    @traitlets.validate('black_box')
    def _check_black_box(self, proposal):
        value = proposal['value']
        if value[0] > value[2] or value[1] > value[3]:
            raise traitlets.TraitError(f'Parameter focus_box is invalid: {value}')
        return value

    @traitlets.validate('synth_video')
    def _validate_value(self, proposal):
        try:
            jsonschema.validate(proposal['value'], self.synth_video_schema)
        except jsonschema.ValidationError as e:
            raise traitlets.TraitError(e)
        return proposal['value']

    def __str__(self):
        str_ = f'_area_thresh: {self._area_thresh} _focus_box: {self._focus_box} _black_box: {self._black_box} '
        str_ += f'_stride: {self._stride} synth_video: {self.synth_video}'
        return str_
