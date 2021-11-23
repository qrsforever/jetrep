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
)


class USBEventMonitor(object):
    
    def __init__(self, native, mntdir='/mnt/usb'):
        self.native = native
        self.mntdir = mntdir
        self._context = Context()
        self._loop = GLib.MainLoop()
        if not os.path.exists(self.mntdir):
            os.makedirs(self.mntdir)

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
            self.native.send_message(MessageType.NOTIFY, NotifyType.USB_MOUNT, 0, self.mntdir)
        if device.action == 'add':
            subprocess.call(['mount', device.device_node, self.mntdir])
            if os.path.ismount(self.mntdir):
                self.native.send_message(MessageType.NOTIFY, NotifyType.USB_MOUNT, 1, self.mntdir)

    def start(self):
        self.usbmon = Monitor.from_netlink(self._context)
        self.usbmon.filter_by('usb', 'usb_device')
        usb_observer = MonitorObserver(self.usbmon)
        usb_observer.connect('device-event', self.handle_usb_event)

        self.blkmon = Monitor.from_netlink(self._context)
        self.blkmon.filter_by('block', 'partition')
        blk_observer = MonitorObserver(self.blkmon)
        blk_observer.connect('device-event', self.handle_blk_event)

        self.usbmon.start()
        self.blkmon.start()

    def stop(self):
        self._loop.quit()

    def loop(self):
        self._loop.run()
