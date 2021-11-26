#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file network.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-26 18:42


from jetrep.core.message import MessageHandler
from jetrep.core.message import (
     MessageType,
     CommandType,
     NetworkType,
     ServiceType,
)
from jetrep.utils.net import (
    util_create_hotspot,
    util_wifi_connect,
    util_get_mac,
)


UNINIT = 0
SUCCESS = 1
FAILURE = 2


class NetworkHandler(MessageHandler):
    def __init__(self, app):
        super(NetworkHandler, self).__init__(app, keys=[
            MessageType.NETWORK, MessageType.STATE
        ])
        self.net_active = UNINIT
        self.jet_apname = 'JET-%s' % util_get_mac()[-6:]

    def on_wifi_connect(self, arg2, obj):
        ssid = obj['ssid']
        pswd = obj['password']
        util_wifi_connect(ssid=ssid, passwd=pswd, apname=self.jet_apname)
        return self.send_message(MessageType.CTRL, CommandType.APP_RESTART)

    def on_connect(self, arg2, obj):
        self.net_active = SUCCESS
        return True

    def on_disconnect(self, arg2, obj):
        # Wifi AP
        self.net_active = FAILURE
        util_create_hotspot(ssid=self.jet_apname)
        return True

    def handle_message(self, what, arg1, arg2, obj):
        if what == MessageType.STATE:
            return self.net_active == FAILURE

        if what == MessageType.NETWORK:
            if self.net_active == UNINIT:
                self.send_message(MessageType.CTRL, CommandType.APP_START, ServiceType.API)
            if arg1 == NetworkType.DISCONNECTED:
                return self.on_disconnect(arg2, obj)
            if arg1 == NetworkType.CONNECTED:
                return self.on_connect(arg2, obj)
            if arg1 == NetworkType.WIFI_CONNECT:
                return self.on_wifi_connect(arg2, obj)

        return False

    @staticmethod
    def instance(app):
        return NetworkHandler(app)
