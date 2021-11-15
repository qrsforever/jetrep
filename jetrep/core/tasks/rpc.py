#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file rpc.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 21:38

import zerorpc
import threading


class ServiceRPC(threading.Thread):

    def __init__(self, app, ip, port):
        super(ServiceRPC, self).__init__()
        self.app = app
        self.ip = ip
        self.port = port
        self.server = None

    def stop(self):
        if self.server:
            try:
                self.server.close()
            except Exception:
                pass

    def run(self):
        self.server = zerorpc.Server(self.app.native)
        self.server.bind(f'tcp://{self.ip}:{self.port}')
        self.server.run()
