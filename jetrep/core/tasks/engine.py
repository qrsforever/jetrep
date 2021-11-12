#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file engine.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 22:19

import sys
import zerorpc
import tensorrt as trt
import queue
import numpy as np
from multiprocessing import Process
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)


class InferProcessRT(Process):
    def __init__(self, app, ip, port):
        super(InferProcessRT, self).__init__()
        self.app = app
        self.remote = zerorpc.Client(
            connect_to='tcp://{}:{}'.format(ip, port),
            timeout=10,
            passive_heartbeat=True)

    def stop(self):
        if self.remote:
            self.remote.close()
        super().stop()

    def send_message(self, what, arg1=-1, arg2=-1, obj=None):
        try:
            self.remote.send_message(what, arg1, arg2, obj)
        except Exception:
            pass

    def run(self):
        sys.path.append('/usr/src/tensorrt/samples/python')
#        import common

        self.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STARTING)
#        try:
#            with open(model_path, "rb") as f, \
#                trt.Runtime(trt.Logger()) as runtime, \
#                runtime.deserialize_cuda_engine(f.read()) as engine, \
#                engine.create_execution_context() as context:
#
#                inputs, outputs, bindings, stream = common.allocate_buffers(engine)
#
#                status_queue.put((101, 'running'))
#                while True:
#                    try:
#                        token, np_frames = batch_queue.get(timeout=timeout)
#                        if token < 0:
#                            status_queue.put((0, 'quit'))
#                            break
#                    except queue.Empty:
#                        continue
#                    except Exception as err:
#                        status_queue.put((-1, f'err: {err}'))
#                        break
#
#                    np_frames = np_frames.astype(np.float32)
#                    np_frames -= 127.5
#                    np_frames /= 127.5
#                    inputs[0].host = np.reshape(np_frames, (1, 64, 112, 112, 3))
#
#                    trt_outputs = common.do_inference_v2(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
#                    trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, ((-1, 1), (-1, 32)))]
#
#                    result_queue.put((token, trt_outputs[0].copy(), trt_outputs[1].copy()))
#        except Exception as err:
#            status_queue.put((-2, f'err: {err}'))
