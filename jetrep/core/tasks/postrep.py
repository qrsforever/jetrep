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
# import threading
from jetrep.utils.ai import (
    sigmoid,
    softmax
)
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
    NotifyType,
    PayloadType,
)
from .base import ServiceBase


class TRTPostrepProcess(ServiceBase):
    name = 'InferPostrep'

    def __init__(self, evt_exit, **kwargs):
        super(TRTPostrepProcess, self).__init__(evt_exit, **kwargs)

    def type(self):
        return ServiceType.RT_INFER_POSTREP

    def task(self, remote, exit, mq_timeout):
        def empirical_kstest(emb, scaler, pca, ecdfs, alpha=0.01):
            out = pca.transform(scaler.transform(emb))
            pvals = np.array([stats.kstest(out[:, i], cdf=lambda x: ecdfs[i](x))[1] for i in range(out.shape[-1])])
            return sum(pca.explained_variance_ratio_[pvals > alpha])

        import pickle
        from scipy import stats
        kgst = [
            'appsrc',
            'videoconvert',
            'video/x-raw,format=BGRx',
            'nvvidconv',
            'nvv4l2h264enc bitrate=500000',
            'video/x-h264,stream-format=(string)byte-stream,alignment=(string)au',
            'h264parse',
        ]
        writer = None
        pcaks = None
        alpha = 0
        remote.send_message(MessageType.STATE, ServiceType.RT_INFER_POSTREP, StateType.STARTED, self.name)
        sumcount = 0
        while not exit.is_set():
            try:
                bucket = self.mQout.get(timeout=mq_timeout)
            except queue.Empty:
                continue
            (width, height), rate = bucket.frame_size, bucket.frame_rate
            if bucket.reset_count:
                sumcount = 0
            if bucket.rtmp_url:
                rtmp_url = bucket.rtmp_url
                gst_str = ' ! '.join(kgst + [
                    'queue',
                    'flvmux streamable=true name=mux',
                    f'rtmpsink max-lateness=500000 location={rtmp_url}'
                ])
                remote.logd(f'Video writer gst: {gst_str}')
                if writer:
                    writer.release()
                writer = cv2.VideoWriter(gst_str, 0, rate, (width, height))

            if bucket.embedding_filter:
                pcaks = None
                try:
                    enable, path, alpha, beta = bucket.embedding_filter
                    if enable and path:
                        pcaks = pickle.load(open(path, 'rb'))
                        pcaks['alpha'] = alpha
                        pcaks['beta'] = beta
                        pcaks['thresh'] = sum(pcaks['pca'].explained_variance_ratio_) / 2
                except Exception as err:
                    remote.loge(f'load embedding filter [{path}] err: {err}')

            final_embs, within_scores, period_scores = bucket.final_embs, bucket.within_scores, bucket.period_scores

            per_frame_periods = np.argmax(period_scores, axis=-1) + 1
            conf_pred_periods = np.max(softmax(period_scores, axis=-1), axis=-1)
            conf_pred_periods = np.where(per_frame_periods < 3, 0.0, conf_pred_periods)

            within_period_scores = sigmoid(within_scores)[:, 0]
            within_period_scores = np.sqrt(within_period_scores * conf_pred_periods)
            if pcaks:
                alpha = pcaks.get('alpha', 0.01)
                beta = pcaks.get('beta', 0.7)
                thresh = pcaks.get('thresh', 0.4)
                factors = np.ones(len(final_embs))
                for i in range(len(final_embs)):
                    emb = final_embs[i]
                    ksret = empirical_kstest(emb, pcaks['scaler'], pcaks['pca'], pcaks['ecdfs'], alpha)
                    if ksret < thresh:
                        factors[i] = beta * ksret / thresh
                remote.logi(f'filter factors: {factors}')
                factors = factors.repeat(64)
                within_period_scores *= factors
            within_period_binary = np.asarray(within_period_scores > 0.5)

            per_frame_counts = within_period_binary * np.where(per_frame_periods < 3, 0.0, 1 / per_frame_periods)

            remote.logi(f'{bucket.raw_frames_path}: {sum(per_frame_counts)}')
            frame_counts = [0] * bucket.raw_frames_count
            s = 0
            for i, t in enumerate(bucket.selected_indices):
                for j in range(s, t):
                    frame_counts[j] = per_frame_counts[i] / (t - s)
                s = t
            if os.path.exists(bucket.raw_frames_path):
                cap = cv2.VideoCapture(bucket.raw_frames_path)
                frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
                if frame_rate != bucket.frame_rate:
                    remote.logw('Conflict frame rate: %d vs %d' % (frame_rate, bucket.frame_rate))
                bucket.cumsum_per_seconds = [] # np.take(frame_counts, range(len(frame_counts), frame_rate))
                frame_counts = np.round(np.cumsum(frame_counts), 3)
                for i, c in enumerate(frame_counts):
                    if i % frame_rate == 0:
                        bucket.cumsum_per_seconds.append(c)
                    retval, frame_bgr = cap.read()
                    if not retval or exit.is_set():
                        break
                    if bucket.black_box:
                        bx1, by1, bx2, by2 = bucket.black_box
                        cv2.rectangle(frame_bgr, (bx1, by1), (bx2, by2), (0, 0, 0), 2)
                    if bucket.focus_box:
                        fx1, fy1, fx2, fy2 = bucket.focus_box
                        cv2.rectangle(frame_bgr, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)

                    cv2.putText(
                        frame_bgr,
                        f'{width}x{height} {rate} S:{bucket.stride} A:{bucket.area_thresh} C:{c + sumcount:.3f}',
                        (int(0.2 * width), int(0.2 * height)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    if pcaks:
                        cv2.putText(
                            frame_bgr,
                            f'Alpha: {pcaks["alpha"]:.3f} Beta: {pcaks["beta"]:.3f}',
                            (int(0.1 * width), int(0.9 * height)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    if writer:
                        writer.write(frame_bgr)
                else:
                    bucket.cumsum_per_seconds.append(c)
                sumcount += frame_counts[-1]

                cap.release()
            if os.path.exists(bucket.raw_frames_path):
                os.unlink(bucket.raw_frames_path)
            del bucket.final_embs, bucket.within_scores, bucket.period_scores
            del bucket.raw_frames_path, bucket.selected_indices
            remote.send_message(MessageType.NOTIFY, NotifyType.TO_CLOUD, PayloadType.REP_INFER_RESULT, bucket)
            del bucket
        if writer:
            writer.release()
