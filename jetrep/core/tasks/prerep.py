#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file prerep.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-15 15:27

import cv2
from jetrep.core.message import (
    MessageType,
    ServiceType,
    StateType,
)
from .base import ServiceBase, DumpDict

DEFAULT_SHM_PATH = '/tmp/gst_repnet.shm'


class TRTPrerepProcess(ServiceBase):
    name = 'InferPrerep'

    def __init__(self, evt_exit, **kwargs):
        self.shm_path = kwargs.pop('shm_path', DEFAULT_SHM_PATH)
        super(TRTPrerepProcess, self).__init__(evt_exit, **kwargs)

    def type(self):
        return ServiceType.RT_INFER_PREREP

    def task(self, remote, exit, mq_timeout):
        width, height, rate = remote.get_props_frame()
        gst_str = ' ! '.join([
            f'shmsrc socket-path={self.shm_path}',
            f'video/x-raw,format=BGR,width={width},height={height},framerate={rate}/1',
            'appsink drop=1'
        ])
        try:
            remote.logi(f'Open cammera: [{gst_str}]')
            cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
            if not cap.isOpened():
                raise RuntimeError('Could not open camera.')
            retval, _ = cap.read()
            if not retval:
                raise RuntimeError('Could not read image from camera.')

            frame_size = (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            remote.logi(f'Frame info: {frame_rate} {frame_size}')
        except Exception:
            raise RuntimeError('Could not initialize camera.  Please see error trace.')

        pre_frame = None
        keep_flag = 1
        bucket = None
        remote.send_message(MessageType.STATE, ServiceType.RT_INFER_PREREP, StateType.STARTED)
        while not exit.is_set():
            try:
                retval, frame_bgr = cap.read()
                if not retval:
                    remote.loge('Cap read error!')
                    break
                if bucket is None:
                    bucket = DumpDict(remote.get_bucket())
                    writer = cv2.VideoWriter(
                        bucket.raw_frames_path,
                        cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, frame_size)

                bucket.raw_frames_count += 1
                writer.write(frame_bgr)

                if bucket.black_box:
                    black_x1, black_y1, black_x2, black_y2 = bucket.black_box
                    frame_bgr[black_y1:black_y2, black_x1:black_x2, :] = 0

                if bucket.focus_box:
                    focus_x1, focus_y1, focus_x2, focus_y2 = bucket.focus_box
                    frame_bgr = frame_bgr[focus_y1:focus_y2, focus_x1:focus_x2, :]

                if bucket.area_thresh > 0:
                    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                    if pre_frame is not None:
                        frame_tmp = cv2.absdiff(frame_gray, pre_frame)
                        frame_tmp = cv2.threshold(frame_tmp, 20, 255, cv2.THRESH_BINARY)[1]
                        frame_tmp = cv2.dilate(frame_tmp, None, iterations=2)
                        contours, _ = cv2.findContours(frame_tmp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                        if len(contours) > 0:
                            for contour in contours:
                                if cv2.contourArea(contour) > bucket.area_thresh:
                                    keep_flag += 1
                                    break
                    pre_frame = frame_gray
                else:
                    keep_flag += 1

                if keep_flag % bucket.stride == 0 or bucket.raw_frames_count > bucket.max_frame_count:
                    frame_bgr = cv2.resize(frame_bgr, (112, 112))
                    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                    if bucket.raw_frames_count > bucket.max_frame_count:
                        diff = 64 - len(bucket.selected_indices)
                        for _ in range(diff):
                            bucket.selected_indices.append(bucket.raw_frames_count - 1)
                            bucket.inputs.append(frame_rgb)
                        remote.logw(f'May be still frames is to many, diff[{diff}].')
                    else:
                        bucket.selected_indices.append(bucket.raw_frames_count - 1)
                        bucket.inputs.append(frame_rgb)
                    if len(bucket.selected_indices) == 64:
                        writer.release(); writer = None # noqa
                        self.mQin.put(bucket)
                        del bucket; bucket = None # noqa
                    keep_flag = 1
            except Exception as err:
                remote.loge(f'Err: {err}')
                break
        if cap.isOpened():
            cap.release()
        remote.send_message(MessageType.STATE, ServiceType.RT_INFER_PREREP, StateType.STOPPED)
