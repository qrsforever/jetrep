#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-22 18:09

import os.path as osp
from traitlets.config.configurable import Configurable
from traitlets import Unicode
import subprocess
from jetrep.constants import DefaultPath


class SoftwareUpgrade(Configurable):

    server_main_url = Unicode('').tag(config=True)
    install_path = Unicode('/var/jetrep/archives').tag(config=True)

    def __init__(self, *args, **kwargs):
        super(SoftwareUpgrade, self).__init__(*args, **kwargs)

    def check_version(self):
        if not self.server_main_url:
            return False
        return False

    def download(self, remote_url=None):
        pass

    def install(self, zip_path):
        update_script = osp.join(DefaultPath.CRONTAB_DIRECTORY, 'update.sh')
        result = subprocess.call(f'{update_script} {zip_path} {self.install_path}', shell=True)
        return result.returncode


__all__ = ["SoftwareUpgrade"]
