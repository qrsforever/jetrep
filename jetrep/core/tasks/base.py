#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file base.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-16 11:29

from jetrep.core import RemoteAgent
from jetrep.core.message import (
    MessageType,
    StateType,
)
from multiprocessing import Process, Event, Lock


class ServiceBase(Process):

    def __init__(self, evt_exit, **kwargs):
        self.exit = evt_exit
        self.mq_timeout = kwargs.pop('mq_timeout', 3)
        for key, val in kwargs.items():
            setattr(self, key, val)
        super(ServiceBase, self).__init__(name=self.name)

        self.exited = Event()
        self.lock = Lock()
        self.lock.acquire()
        super().start()

    @property
    def clsname(self):
        return self.__class__.__name__

    def type(self):
        raise RuntimeError('Not imple subclass method')

    def on_destroy(self):
        pass

    def start(self):
        self.lock.release()

    def stop(self, handler):
        try:
            self.lock.release() # TODO call stop before start
        except Exception:
            pass
        handler.send_message(MessageType.STATE, self.type(), StateType.STOPPING, self.clsname)
        self.exited.wait(timeout=2*self.mq_timeout)
        if not self.exited.is_set():
            handler.send_message(MessageType.STATE, self.type(), StateType.STOPPTIMEOUT, self.clsname)
        self.join(0.5)

    def run(self):
        import signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        self.lock.acquire()
        while self.exit.is_set():
            return
        import traceback
        remote = self.initialize()
        if remote:
            remote.logi(f'Process {self.name} is starting...')
            remote.send_message(MessageType.STATE, self.type(), StateType.STARTING, self.clsname)
            try:
                self.task(remote, self.exit, self.mq_timeout)
                remote.send_message(MessageType.STATE, self.type(), StateType.STOPPED, self.clsname)
            except Exception:
                remote.loge(f'{traceback.format_exc(limit=6)}')
                remote.send_message(MessageType.STATE, self.type(), StateType.CRASHED, self.clsname)
            finally:
                self.on_destroy()
                remote.logw(f'Process {self.name} is finished...')
                remote.close()
        else:
            raise RuntimeError('Can not connect rpc server')
        self.exited.set()

    @property
    def mQin(self):
        return self.mq_in

    @property
    def mQout(self):
        return self.mq_out

    def initialize(self):
        import zerorpc
        return RemoteAgent(
                zerorpc.Client(
                    connect_to='tcp://{}:{}'.format(self.ip, self.port),
                    timeout=10,
                    passive_heartbeat=True))

    def task(self, remote, exit, mq_timeout):
        raise RuntimeError('Sub class must impl.')


if __name__ == "__main__":
    s = ServiceBase(ip='0.0.0.0', port=8888, name='test')
    print(s.ip, s.port)
