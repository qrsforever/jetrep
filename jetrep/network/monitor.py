#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file monitor.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-25 18:12


import time
import datetime
import threading

from jetrep.utils.net import util_ping_request
from jetrep.utils.misc import util_delta_time


class ConnectMonitor(threading.Thread):
    def __init__(self, logger, on_connect, on_disconnect, ping_freq=(30, 1)):
        super(ConnectMonitor, self).__init__()
        self.logger = logger
        self.ping_freq = ping_freq
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

    def run(self):
        start_time = datetime.datetime.now()
        self.logger.info(f'Monitoring started at: {str(start_time).split(".")[0]}')
        is_connected = False
        while True:
            if util_ping_request():
                if not is_connected:
                    is_connected = True
                    self.on_connect()
                time.sleep(self.ping_freq[0])
                self.on_disconnect() # TODO test
            else:
                is_connected = False
                down_time = datetime.datetime.now()
                self.logger.info(f'Connection Unavailable at: {str(down_time).split(".")[0]}')
                i = 0
                while not util_ping_request():
                    i += 1
                    time.sleep(self.ping_freq[1])
                    if i % 101 == 0: 
                        now = datetime.datetime.now()
                        self.logger.info(f'Unavailabilty Persistent at: {str(now).split(".")[0]}')
                    if i == 3:
                        self.on_disconnect()

                up_time = datetime.datetime.now()
                self.logger.info(f'Connection Restored at: {str(up_time).split(".")[0]} {util_delta_time(down_time, up_time)}')

        self.logger.warning(f'Monitoring Finished!!!')
