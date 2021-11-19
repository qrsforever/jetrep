#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file engine.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 22:19

import queue
import numpy as np
from .base import ServiceBase
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)

DEFAULT_WGT_PATH = '/home/nano/models/repnet_b1.trt'


class TRTEngineProcess(ServiceBase):
    name = 'InferEngine'

    def __init__(self, evt_exit, **kwargs):
        self.weight_path = kwargs.pop('weight_path', DEFAULT_WGT_PATH)
        super(TRTEngineProcess, self).__init__(evt_exit, **kwargs)

    def type(self):
        return ServiceType.RT_INFER_ENGINE

    def on_destroy(self):
        # TODO cuda engine quit problem
        import os, signal
        os.kill(os.getpid(), signal.SIGKILL)

    def task(self, remote, exit, mq_timeout):
        import sys
        sys.path.append('/usr/src/tensorrt/samples/python')

        # import pycuda.driver as cuda
        import tensorrt as trt
        import common

        remote.logi('Create engine context.')
        # cuda.init()
        # device = cuda.Device(0)
        # ctx = device.make_context()
        with open(self.weight_path, "rb") as f, \
            trt.Runtime(trt.Logger()) as runtime, \
            runtime.deserialize_cuda_engine(f.read()) as engine, \
            engine.create_execution_context() as context: # noqa

            inputs, outputs, bindings, stream = common.allocate_buffers(engine)

            remote.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STARTED)
            while not exit.is_set():
                try:
                    bucket = self.mQin.get(timeout=mq_timeout)
                except queue.Empty:
                    continue

                np_frames = np.asarray(bucket.inputs, dtype=np.float32)
                np_frames -= 127.5
                np_frames /= 127.5
                inputs[0].host = np.reshape(np_frames, (1, 64, 112, 112, 3))

                trt_outputs = common.do_inference_v2(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
                trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, ((-1, 1), (-1, 32)))]

                bucket.within_scores = trt_outputs[0].copy()
                bucket.period_scores = trt_outputs[1].copy()

                del bucket.inputs
                self.mQout.put(bucket)

            del context, inputs, outputs, bindings, stream
        # ctx.pop()
        # del ctx
