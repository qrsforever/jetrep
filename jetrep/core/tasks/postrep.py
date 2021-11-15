#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file postrep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-15 17:27

import cv2, os
import numpy as np
import queue
import threading
from jetrep.utils.ai import (
    sigmoid,
    softmax
)
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)


class PostProcessRep(threading.Thread):
    """
    Postprocess inputs before repnet rt
    """
    def __init__(self, app, mq_in, mq_out):
        super(PostProcessRep, self).__init__(name=app.tsk_name_postrep)
        self.app = app
        self.mq_in, self.mq_out = mq_in, mq_out
        self.exit = False

    def start(self):
        self.app.native.send_message(MessageType.STATE, ServiceType.RT_INFER_POSTREP, StateType.STARTING)
        super().start()

    def stop(self):
        self.app.native.send_message(MessageType.STATE, ServiceType.RT_INFER_POSTREP, StateType.STOPPING)
        self.exit = True

    def run(self):
        ctx, native = self.app.psctx, self.app.native

        native.logi("Start postrep_process_worker...")
    
        gst_str = ' ! '.join([
            'appsrc',
            'videoconvert',
            'video/x-raw,format=BGRx',
            'nvvidconv',
            'nvv4l2h264enc bitrate=4000000',
            'video/x-h264,stream-format=(string)byte-stream,alignment=(string)au',
            'h264parse',
            'queue',
            'flvmux streamable=true name=mux',
            'rtmpsink max-lateness=500000 location=rtmp://0.0.0.0:1935/live/post_test'
        ])
        writer = cv2.VideoWriter(gst_str, 0, ctx.frame_rate, ctx.frame_size)

        native.send_message(MessageType.STATE, ServiceType.RT_INFER_POSTREP, StateType.STARTED)
        sumcount = 0
        while not self.exit:
            try:
                token, bucket = self.mq_out.get(timeout=3)
            except queue.Empty:
                continue
            except Exception as err:
                native.loge(f'Err: {err}')
                break

            within_scores, period_scores = bucket.within_scores, bucket.period_scores
            
            per_frame_periods = np.argmax(period_scores, axis=-1) + 1
            conf_pred_periods = np.max(softmax(period_scores, axis=-1), axis=-1)
            conf_pred_periods = np.where(per_frame_periods < 3, 0.0, conf_pred_periods)
                
            within_period_scores = sigmoid(within_scores)[:, 0]
            within_period_scores = np.sqrt(within_period_scores * conf_pred_periods)
            within_period_binary = np.asarray(within_period_scores > 0.5)
            
            per_frame_counts = within_period_binary * np.where(per_frame_periods < 3, 0.0, 1 / per_frame_periods)

            native.logi(f'{bucket.raw_frames_path}: {sum(per_frame_counts)}')
            frame_counts = [0] * bucket.raw_frames_count
            s = 0
            for i, t in enumerate(bucket.selected_indices):
                for j in range(s, t):
                    frame_counts[j] = per_frame_counts[i] / (t - s)
                s = t
            if os.path.exists(bucket.raw_frames_path):
                cap = cv2.VideoCapture(bucket.raw_frames_path)
                frame_counts = np.cumsum(frame_counts) + sumcount
                for c in frame_counts:
                    retval, frame_bgr = cap.read()
                    if not retval:
                        break
                    cv2.putText(frame_bgr, f'%.3f' % c, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    writer.write(frame_bgr)
                else:
                    sumcount = c
                cap.release()
                os.unlink(bucket.raw_frames_path)
            del bucket
        writer.release()    
        native.logw('PostRep process worker end!')
        native.send_message(MessageType.STATE, ServiceType.RT_INFER_POSTREP, StateType.STOPPED)
