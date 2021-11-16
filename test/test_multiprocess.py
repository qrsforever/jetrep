#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, signal
import multiprocessing
from multiprocessing import Process, Event
from multiprocessing import Pool # noqa
import time


multiprocessing.set_start_method('forkserver', force=True)


class ProcessA(Process):
    def __init__(self, name, exit_event):
        super(ProcessA, self).__init__(name=name)
        self.exit_event = exit_event

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        while not self.exit_event.is_set():
            print(self.name)
            time.sleep(1)
        print('end!')


def signal_handler(sig, frame):
    exit_event.set()
    os._exit(os.EX_OK)


if __name__ == "__main__":
    exit_event = Event()
    # signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)
    processes = []
    for i in range(3):
        processes.append(ProcessA('proc-%d' % i, exit_event))
    for proc in processes:
        proc.start()

    try:
        time.sleep(5)
        # exit_event.set()
        # time.sleep(3)

        for proc in processes:
            print('before join:', proc.is_alive())
            # proc.join()
            # print('after join:', proc.is_alive())
        time.sleep(10)
    except KeyboardInterrupt:
        exit_event.set()
