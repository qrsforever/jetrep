#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file event.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-23 14:01

import os
import subprocess
from pyudev import Context, Monitor
from gi.repository import GLib
from pyudev.glib import MonitorObserver
from jetrep.core.message import (
    MessageType,
    NotifyType,
    PayloadType,
    NetworkType,
)

import time
import datetime
import threading

from jetrep.utils.net import util_ping_request
from jetrep.utils.misc import util_delta_time


class SystemEventMonitor(threading.Thread):

    def __init__(self, native, evt_exit, mntdir='/mnt/usb', ping_freq=(10, 1)):
        super(SystemEventMonitor, self).__init__(name='systemevent')
        self.exit = evt_exit
        self.native = native
        self.mntdir = mntdir
        self.ping_freq = ping_freq
        self._context = Context()
        self._loop = GLib.MainLoop()

    def setup(self):
        if not os.path.exists(self.mntdir):
            os.makedirs(self.mntdir)

        self.netmon = Monitor.from_netlink(self._context)
        self.netmon.filter_by('net')
        MonitorObserver(self.netmon).connect('device-event', self.handle_net_event)

        self.usbmon = Monitor.from_netlink(self._context)
        self.usbmon.filter_by('usb', 'usb_device')
        MonitorObserver(self.usbmon).connect('device-event', self.handle_usb_event)

        self.blkmon = Monitor.from_netlink(self._context)
        self.blkmon.filter_by('block', 'partition')
        MonitorObserver(self.blkmon).connect('device-event', self.handle_blk_event)

    def start(self):
        self.netmon.start()
        self.usbmon.start()
        self.blkmon.start()
        super().start()

    def stop(self):
        self._loop.quit()

    def loop(self):
        self._loop.run()

    def handle_net_event(self, observer, device):
        self.native.logi(f'{device.action}')

    def handle_usb_event(self, observer, device):
        if device.action not in ['add', 'remove']:
            return
        self.native.logd(f'{device.device_type}, {device.driver}')

    def handle_blk_event(self, observer, device):
        if device.action not in ['add', 'remove']:
            return
        self.native.logd(f'{device.device_type}, {device.driver}')

        if not device.device_node.startswith('/dev/sd'):
            # TODO if 'ID_BUS' in x and x['ID_BUS'] == 'usb'
            return

        # usb mount
        if os.path.ismount(self.mntdir):
            subprocess.call(['umount', '-l', self.mntdir])
            self.native.send_message(MessageType.NOTIFY, NotifyType.USB_MOUNT, PayloadType.UNMOUNTED, self.mntdir)
        if device.action == 'add':
            subprocess.call(['mount', device.device_node, self.mntdir])
            if os.path.ismount(self.mntdir):
                self.native.send_message(MessageType.NOTIFY, NotifyType.USB_MOUNT, PayloadType.MOUNTED, self.mntdir)

    def run(self):
        start_time = datetime.datetime.now()
        self.native.logi(f'Monitoring started at: {str(start_time).split(".")[0]}')
        is_connected = False
        while not self.exit.is_set():
            if util_ping_request():
                if not is_connected:
                    is_connected = True
                    self.native.send_message(MessageType.NETWORK, NetworkType.CONNECTED)
                time.sleep(self.ping_freq[0])
            else:
                is_connected = False
                down_time = datetime.datetime.now()
                self.native.logi(f'Connection Unavailable at: {str(down_time).split(".")[0]}')
                i = 0
                while not util_ping_request():
                    i += 1
                    time.sleep(self.ping_freq[1])
                    if i % 101 == 0:
                        now = datetime.datetime.now()
                        self.native.logw(f'Unavailabilty Persistent at: {str(now).split(".")[0]}')
                    if i == 2:
                        self.native.send_message(MessageType.NETWORK, NetworkType.DISCONNECTED)

                up_time = datetime.datetime.now()
                self.native.logi(f'Connection Restored at: {str(up_time).split(".")[0]} {util_delta_time(down_time, up_time)}')

        self.native.logw(f'System Event Monitoring Finished!!!')
