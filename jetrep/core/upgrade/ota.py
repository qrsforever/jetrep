#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ota.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-24 11:33

import os
import threading
import requests, json
import shutil
import subprocess
from jetrep.constants import DefaultPath as DP
from jetrep.constants import APP_VERSION_INFO
from jetrep.core.message import (
    MessageType,
    UpgradeType,
    PayloadType,
)


def compare_version(vnew, vold):
    if vnew == vold:
        return False
    new = vnew.split('.')
    old = vold.split('.')
    for i in range(min(len(new), len(old))):
        if int(new[i]) > int(old[i]):
            return True
    return False


class OtaUpgrade(threading.Thread):

    def __init__(self, native, server_url, conn_timeout, read_timeout):
        super(OtaUpgrade, self).__init__(name='OtaUpgrade', daemon=True)
        self.native = native
        self.server_url = server_url
        self.conn_timeout = conn_timeout
        self.read_timeout = read_timeout

    def check_update(self):
        '''
        Request update config file
        {
            "version":"xxx.xxx.xxx",
            "url":"http://xxx.xxx.xxx.zip",
            "md5":"xxx",
            "datetime": "xxx",
            "content":"jetrep config file not update",
            "compatible": true,
            "force": false
        }
        '''
        if self.server_url:
            response = requests.get(self.server_url,
                    headers={'Content-Type': 'application/json'},
                    timeout=(self.conn_timeout, self.read_timeout))
            if response.status_code == 200:
                config = response.json()
                self.native.logi(config)
                if config.get('force', False) or compare_version(config['version'], APP_VERSION_INFO['version']):
                    with open(DP.UPDATE_CONFIG_PATH, 'w') as fw:
                        fw.write(json.dumps(config, indent=4))
                    return config
            else:
                self.native.loge('Request update config [%s] error!' % self.server_url)
        return None

    def run(self):
        self.native.logi('Start OtaUpgrade Thread')
        # 1. check
        update_config = self.check_update()
        if update_config is None:
            self.native.logi('Finish OtaUpgrade Thread (update is not needed)')
            return
        zip_url = update_config['url']
        zip_md5 = update_config['md5']
        dst_dir = f'{DP.UPDATE_INSTALL_PATH}/{update_config["version"]}'
        try:
            # 2. download
            zip_res = requests.get(zip_url,
                    headers={'Content-Type': 'application/zip'},
                    timeout=(self.conn_timeout, self.read_timeout))
            if zip_res.status_code != 200:
                raise RuntimeError('OtaUpgrade request zip file error!')
            with open(DP.UPDATE_ZIP_PATH, 'wb') as fw:
                fw.write(zip_res.content)
            self.native.logi('OtaUpgrade [%s] downloaded!' % zip_url)
            md5 = subprocess.check_output(f'md5sum {DP.UPDATE_ZIP_PATH} | cut -c1-32', shell=True)
            if md5.decode('utf-8').strip() != zip_md5:
                raise RuntimeError('OtaUpgrade zip md5 not match!')
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            # 3. unzip
            subprocess.call(f'unzip -qo {DP.UPDATE_ZIP_PATH} -d {dst_dir}', shell=True)
            if update_config.get('compatible', True):
                shutil.copy(DP.JETREP_CONF_PATH, f'{dst_dir}/{DP.APP_NAME}/{DP.RUNTIME_NAME}/')

            # 4. install(soft link)
            os.remove(DP.APP_LINK)
            os.symlink(f'{dst_dir}/{DP.APP_NAME}', DP.APP_LINK)

            # 5. notify message
            self.native.send_message(MessageType.UPGRADE, UpgradeType.OTA, PayloadType.UPGRADE_SUCCESS)

        except subprocess.CalledProcessError as exc:
            payload = f'Run subprocess: {exc.cmd} returncode: {exc.returncode}'
            self.native.send_message(MessageType.UPGRADE, UpgradeType.OTA, PayloadType.UPGRADE_ERROR, payload)
        except Exception as err:
            self.native.send_message(MessageType.UPGRADE, UpgradeType.OTA, PayloadType.UPGRADE_ERROR, f'{err}')
        finally:
            if os.path.exists(DP.UPDATE_ZIP_PATH):
                os.remove(DP.UPDATE_ZIP_PATH)
        self.native.logi('OtaUpgrade thread quit!')
