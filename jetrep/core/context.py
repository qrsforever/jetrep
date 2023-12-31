#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file context.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-15 15:40

import os, sys
import time
import shutil
import jsonschema
import traitlets
import os.path as osp
from traitlets.config.configurable import LoggingConfigurable
from traitlets import Int, Float, Unicode, Tuple, List, Dict, Bool
from jetrep.constants import DefaultServer, DefaultPath, DefaultPSContext
from jetrep.utils.net import util_get_mac, util_request_data


class PSContext(LoggingConfigurable):
    frame_size = Tuple((640, 480))
    frame_rate = Int(30)
    focus_box = List(Float(min=0., max=1.), [0.0, 0.0, 1.0, 1.0], minlen=4, maxlen=4).tag(config=True)
    black_box = List(Float(min=0., max=1.), [0.0, 0.0, 0.0, 0.0], minlen=4, maxlen=4).tag(config=True)
    area_rate = Float(default_value=0.002, min=0.0, max=0.05).tag(config=True)
    max_duration = Int(30).tag(config=True)
    reset_count = Bool(False).tag(config=True)
    strides = List(trait=Int(), default_value=[4], minlen=1, maxlen=3).tag(config=True)
    video_clips_path = Unicode(DefaultPath.VIDEO_CLIPS_PATH).tag(config=True)

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
                     'duration' : {'type' : 'number'},
                 },
                 'required': ['server']
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

    embedding_filter_schema = {
        'type': 'object',
        'properties': {
            'enable': {'type': 'boolean'},
            'url': {'type': 'string'},
            'alpha': {'type': 'number'},
            'beta': {'type': 'number'}
        },
        'required': ['enable', 'url']
    }
    embedding_filter = Dict().tag(config=True)

    F = 64

    def __init__(self, native, *args, **kwargs):
        self.native = native
        self._focus_box = None
        self._black_box = None
        self._stride = 4
        self._area_thresh = 0
        self._rtmp_url = None
        self._embedding_filter = None
        super(PSContext, self).__init__(*args, **kwargs)

    def setup(self):
        if os.path.exists(self.video_clips_path):
            shutil.rmtree(self.video_clips_path)
        os.makedirs(self.video_clips_path)

    class FBucket(dict):
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

        def __init__(self, video_clips_path, *args, **kwargs):
            super(PSContext.FBucket, self).__init__(*args, **kwargs)
            self.start_time = int(time.time())
            self.raw_frames_count = 0
            self.raw_frames_path = f'{video_clips_path}/{self.start_time}.mp4'
            self.inputs = []
            self.selected_indices = []
            for arg in args:
                if isinstance(arg, dict):
                    for k, v in arg.items():
                        self[k] = v
            if kwargs:
                for k, v in kwargs.items():
                    self[k] = v

        def __getstate__(self):
            return self.__dict__

        def __setstate__(self, d):
            self.__dict__.update(d)

    def make_bucket(self):
        bucket = self.FBucket(self.video_clips_path)
        bucket.frame_size = self.frame_size
        bucket.frame_rate = self.frame_rate
        bucket.focus_box = self._focus_box
        bucket.black_box = self._black_box
        bucket.stride = self._stride
        bucket.area_thresh = self._area_thresh
        bucket.terminal_time = bucket.start_time + self.max_duration
        bucket.reset_count = self.reset_count
        bucket.rtmp_url = self._rtmp_url
        bucket.embedding_filter = self._embedding_filter
        self.native.logd(bucket)
        if self.reset_count:
            self.reset_count = False
        self._rtmp_url = None
        self._embedding_filter = None
        return bucket

    @staticmethod
    def calc_rect_box(w, h, box):
        return [int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])]

    @traitlets.observe('synth_video')
    def _on_synth_video(self, change):
        conf = change['new']
        if 'rtmp' in conf:
            server = conf['rtmp'].get('server')
            port = conf['rtmp'].get('port', DefaultServer.RTMP_PORT)
            stream = conf['rtmp'].get('stream', util_get_mac())
            duration = conf['rtmp'].get('duration', DefaultServer.RTMP_DVR_DURATION)
            self._rtmp_url = f'rtmp://{server}:{port}/post/{stream}?vhost=jet{duration}'
        else:
            pass

    @traitlets.observe('embedding_filter')
    def _on_embedding_filter(self, change):
        conf = change['new']
        url = conf.get('url')
        enable = conf.get('enable')
        try:
            if not enable:
                self._embedding_filter = (0, 0, 0, 0)
            else:
                basepath = os.path.basename(url)
                pkl_path = os.path.join(DefaultPSContext.EF_PKL_PATH, basepath)
                if not os.path.exists(pkl_path):
                    pkl_path = util_request_data(url, path=pkl_path)
                alpha = conf.get('alpha', DefaultPSContext.EF_ALPHA)
                beta = conf.get('beta', DefaultPSContext.EF_BETA)
                self._embedding_filter = (1, pkl_path, alpha, beta)
        except Exception:
            pass

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
        x1, y1, x2, y2 = self._focus_box
        self._area_thresh = int((x2 - x1) * (y2 - y1) * self.area_rate)

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
            self._area_thresh = int((x2 - x1) * (y2 - y1) * change['new'])
            return
        self._area_thresh = int(self.frame_size[0] * self.frame_size[1] * change['new'])

    @traitlets.observe('strides')
    def _on_strides(self, change):
        # TODO only support one stride
        self._stride = change['new'][0]

    @traitlets.validate('focus_box')
    def _check_focus_box(self, proposal):
        value = proposal['value']
        self.native.logd(value)
        if value[0] >= value[2] or value[1] >= value[3]:
            raise traitlets.TraitError(f'focus_box invalid: {value}')
        return value

    @traitlets.validate('black_box')
    def _check_black_box(self, proposal):
        value = proposal['value']
        self.native.logd(value)
        if value[0] > value[2] or value[1] > value[3]:
            raise traitlets.TraitError(f'Parameter focus_box is invalid: {value}')
        return value

    @traitlets.validate('video_clips_path')
    def _validate_video_clips_path(self, proposal):
        value = proposal['value']
        self.native.logd(value)
        if not value.endswith('videos'):
            value = os.path.join(value, 'videos')
        os.makedirs(value, exist_ok=True)
        return value

    @traitlets.validate('synth_video')
    def _validate_synth_video(self, proposal):
        value = proposal['value']
        self.native.logd(value)
        try:
            jsonschema.validate(value, self.synth_video_schema)
        except jsonschema.ValidationError as e:
            raise traitlets.TraitError(e)
        return proposal['value']

    @traitlets.validate('embedding_filter')
    def _validate_embedding_filter(self, proposal):
        value = proposal['value']
        self.native.logd(value)
        try:
            jsonschema.validate(value, self.embedding_filter_schema)
        except jsonschema.ValidationError as e:
            raise traitlets.TraitError(e)
        return proposal['value']

    def __str__(self):
        str_ = f'_area_thresh: {self._area_thresh} _focus_box: {self._focus_box} _black_box: {self._black_box} '
        str_ += f'_stride: {self._stride} synth_video: {self.synth_video}'
        return str_


class RemoteAgent(object):
    def __init__(self, remote):
        self.impl = remote

    def __getattr__(self, method):
        return lambda *args, **kwargs: self.impl(method, *args, **kwargs)

    def close(self):
        return self.impl.close()

    def logd(self, s):
        filename = osp.basename(sys._getframe().f_back.f_code.co_filename)
        lineno = sys._getframe().f_back.f_lineno
        return self.impl.logd(f'[{os.getpid()}] {filename}:{lineno} --> {s}', True)

    def logi(self, s):
        filename = osp.basename(sys._getframe().f_back.f_code.co_filename)
        lineno = sys._getframe().f_back.f_lineno
        return self.impl.logi(f'[{os.getpid()}] {filename}:{lineno} --> {s}', True)

    def logw(self, s):
        filename = osp.basename(sys._getframe().f_back.f_code.co_filename)
        lineno = sys._getframe().f_back.f_lineno
        return self.impl.logw(f'[{os.getpid()}] {filename}:{lineno} --> {s}', True)

    def loge(self, s):
        filename = osp.basename(sys._getframe().f_back.f_code.co_filename)
        lineno = sys._getframe().f_back.f_lineno
        return self.impl.loge(f'[{os.getpid()}] {filename}:{lineno} --> {s}', True)

    def logc(self, s):
        filename = osp.basename(sys._getframe().f_back.f_code.co_filename)
        lineno = sys._getframe().f_back.f_lineno
        return self.impl.logc(f'[{os.getpid()}] {filename}:{lineno} --> {s}', True)
