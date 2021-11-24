#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file udisk.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-24 21:59

import glob
import os
import threading
import shutil
import subprocess
from jetrep.constants import DefaultPath as DP
from jetrep.core.message import (
    MessageType,
    UpgradeType,
    PayloadType,
)


class UDiskUpgrade(threading.Thread):

    def __init__(self, native, mntdir):
        super(UDiskUpgrade, self).__init__(name='UDiskUpgrade', daemon=True)
        self.native = native
        self.mntdir = mntdir

    def run(self):
        self.native.logi('UDiskUpgrade thread start!')
        version = ''
        # 1. check update zip file
        zips = glob.glob(f'{self.mntdir}/update_*.zip')
        for zpath in zips:
            zfile = os.path.basename(zpath)
            version = zfile.split('_')[1][:-4]
            if len(version.split('.')) > 2:
                break
        if not version:
            return

        dst_dir = f'{DP.UPDATE_INSTALL_PATH}/{version}'

        # 2. unzip
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        subprocess.call(f'unzip -qo {zpath} -d {dst_dir}', shell=True)
        shutil.copy(DP.JETREP_CONF_PATH, f'{dst_dir}/{DP.APP_NAME}/{DP.RUNTIME_NAME}/')

        # 3. install(soft link)
        os.remove(DP.APP_LINK)
        os.symlink(f'{dst_dir}/{DP.APP_NAME}', DP.APP_LINK)

        # 4. notify message
        self.native.send_message(MessageType.UPGRADE, UpgradeType.UDISK, PayloadType.UPGRADE_SUCCESS)

        self.native.logi('UDiskUpgrade thread quit!')
