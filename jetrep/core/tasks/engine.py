#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file engine.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 22:19

import sys, time, signal
import zerorpc
import queue
import numpy as np
from multiprocessing import Process, Event
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)


class InferProcessRT(Process):
    def __init__(self, app, ip, port, mq_in, mq_out, weight_path='/home/nano/models/repnet_b1.trt'):
        super(InferProcessRT, self).__init__(name=app.tsk_name_engine)
        # self.native = app.native    # TODO cannot pickle object between process
        self.ip, self.port = ip, port
        self.weight_path = weight_path
        self.mq_in, self.mq_out = mq_in, mq_out
        self.exit = Event()

    # def start(self):
    #     self.native.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STARTING)
    #     super().start()

    def stop(self):
        # self.native.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STOPPING)
        self.exit.set()
        for i in range(15):
            self.mq_in.put((-1, None))
            if not self.is_alive():
                break
            time.sleep(1)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        remote = zerorpc.Client(
            connect_to='tcp://{}:{}'.format(self.ip, self.port),
            timeout=10,
            passive_heartbeat=True)
        sys.path.append('/usr/src/tensorrt/samples/python')

        import tensorrt as trt
        import common

        remote.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STARTING)
        try:
            remote.logi('Create engine context.')
            with open(self.weight_path, "rb") as f, \
                trt.Runtime(trt.Logger()) as runtime, \
                runtime.deserialize_cuda_engine(f.read()) as engine, \
                engine.create_execution_context() as context: # noqa

                inputs, outputs, bindings, stream = common.allocate_buffers(engine)

                remote.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STARTED)
                while not self.exit.is_set():
                    try:
                        token, bucket = self.mq_in.get(timeout=3)
                        if token < 0:
                            break
                    except queue.Empty:
                        continue
                    except Exception as err:
                        remote.loge(err)

                    np_frames = np.asarray(bucket.inputs, dtype=np.float32)
                    np_frames -= 127.5
                    np_frames /= 127.5
                    inputs[0].host = np.reshape(np_frames, (1, 64, 112, 112, 3))

                    trt_outputs = common.do_inference_v2(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
                    trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, ((-1, 1), (-1, 32)))]

                    bucket.within_scores = trt_outputs[0].copy()
                    bucket.period_scores = trt_outputs[1].copy()

                    self.mq_out.put((token, bucket))
        except Exception as err:
            remote.loge(err)
        if remote:
            remote.send_message(MessageType.STATE, ServiceType.RT_INFER_ENGINE, StateType.STOPPED)
            remote.close()
