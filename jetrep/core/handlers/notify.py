#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file notify.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-19 21:38


import os
import shutil
from jetrep.core.message import MessageHandler
from jetrep.constants import DefaultPath as DP
from jetrep.core.message import (
     MessageType,
     CommandType,
     NotifyType,
     TimerType,
     UpgradeType,
     PayloadType,
)


class NotifyHandler(MessageHandler):
    def __init__(self, app):
        super(NotifyHandler, self).__init__(app, keys=[
            MessageType.NOTIFY,
            MessageType.TIMER,
            MessageType.UPGRADE,
        ])
        self.config_is_valid = False
        self.test_max_duration = 30

    def on_conf_event(self, arg2, obj):
        if arg2 == PayloadType.CONFIG_VALID:
            self.app.psctx.max_duration = self.test_max_duration
            if not os.path.exists(DP.CONFIG_VALID_NOD):
                os.mknod(DP.CONFIG_VALID_NOD)
            self.config_is_valid = True
            return True
        if arg2 in (PayloadType.CONFIG_UPDATE, PayloadType.CONFIG_LOADED):
            self.test_max_duration = self.app.psctx.max_duration
            self.app.psctx.max_duration = 5
            if os.path.exists(DP.CONFIG_VALID_NOD):
                os.remove(DP.CONFIG_VALID_NOD)
            self.config_is_valid = False
            return True
        return False

    def on_cloud_event(self, arg2, obj):
        if arg2 == PayloadType.APP_VERSION:
            return True
        elif arg2 == PayloadType.REP_INFER_RESULT:
            if not self.config_is_valid:
                self.send_message(MessageType.NOTIFY, NotifyType.APP_CONF, PayloadType.CONFIG_VALID)
            return True
        return False

    def on_usb_event(self, arg2, obj):
        if arg2 == PayloadType.MOUNTED: # Mount
            return self.app.softu.start_udisk(obj)
        return False

    def on_upgrade_event(self, arg2, obj):
        if arg2 == PayloadType.UPGRADE_ERROR:
            pass
        elif arg2 == PayloadType.UPGRADE_SUCCESS:
            self.do_version_archives()
            return self.send_message(MessageType.CTRL, CommandType.APP_RESTART)
        return False

    def do_version_archives(self):
        archives = sorted(os.listdir(DP.UPDATE_INSTALL_PATH), reverse=True)
        for oldver in archives[5:]:
            shutil.rmtree(os.path.join(DP.UPDATE_INSTALL_PATH, oldver))

    def handle_message(self, what, arg1, arg2, obj):
        if what == MessageType.NOTIFY:
            if arg1 == NotifyType.APP_CONF:
                return self.on_conf_event(arg2, obj)
            if arg1 == NotifyType.TO_CLOUD:
                return self.on_cloud_event(arg2, obj)
            if arg1 == NotifyType.USB_MOUNT:
                return self.on_usb_event(arg2, obj)
            return False

        if what == MessageType.TIMER:
            if arg1 == TimerType.CHECK_UPDATE:
                return self.app.softu.start_ota()
            return False

        if what == MessageType.UPGRADE:
            if arg1 in (UpgradeType.OTA, UpgradeType.UDISK):
                return self.on_upgrade_event(arg2, obj)
            return False

        return False

    @staticmethod
    def instance(app):
        return NotifyHandler(app)
