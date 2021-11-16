#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file base.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-16 11:29

from jetrep.core import RemoteWraper
from multiprocessing import Process, Event, Lock


class DumpDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
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


class ServiceBase(Process):

    def __init__(self, **kwargs):
        self.mq_timeout = kwargs.pop('mq_timeout', 3)
        for key, val in kwargs.items():
            setattr(self, key, val)
        super(ServiceBase, self).__init__(name=self.name)

        self.exited = Event()
        self.exit = Event()
        self.lock = Lock()
        self.lock.acquire()
        super().start()

    @property
    def clsname(self):
        return self.__class__.__name__

    def start(self):
        self.lock.release()

    def stop(self):
        self.lock.release()
        self.exit.set()
        self.exited.wait(timeout=2*self.mq_timeout)
        self.join(0.5)

    def run(self):
        self.lock.acquire()
        remote = self.initialize()
        if remote:
            remote.logi(f'Process {self.name} is starting...')
            self.task(remote, self.exit, self.mq_timeout)
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
        import signal, zerorpc

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)

        return RemoteWraper(
                zerorpc.Client(
                    connect_to='tcp://{}:{}'.format(self.ip, self.port),
                    timeout=10,
                    passive_heartbeat=True))

    def task(self, remote, exit, mq_timeout):
        raise RuntimeError('Sub class must impl.')


if __name__ == "__main__":
    s = ServiceBase(ip='0.0.0.0', port=8888, name='test')
    print(s.ip, s.port)
