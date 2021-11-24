#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-22 18:09

from traitlets.config.configurable import Configurable
from traitlets import Unicode, Float
from .ota import OtaUpgrade


class SoftwareUpgrade(Configurable):
    server_url = Unicode('http://172.16.0.35/softu/update_config.json', help='Set upgrade server url').tag(config=True)
    conn_timeout = Float(3, help='Set timeout(s) for request connect').tag(config=True)
    read_timeout = Float(3, help='Set timeout(s) for request read payload').tag(config=True)

    def __init__(self, native, *args, **kwargs):
        self.native = native
        super(SoftwareUpgrade, self).__init__(*args, **kwargs)

    def setup(self):
        pass

    def start_ota(self):
        ota = OtaUpgrade(self.native, self.server_url, self.conn_timeout, self.read_timeout)
        ota.start()
        return True


__all__ = ["SoftwareUpgrade"]
