#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ota.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-24 11:33

import os
import traceback
import threading
import requests, json
import shutil
import subprocess
from jetrep.constants import DefaultPath as DP
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

    def __init__(self, native, app_version, server_url, conn_timeout, read_timeout):
        super(OtaUpgrade, self).__init__(name='OtaUpgrade', daemon=True)
        self.native = native
        self.app_version = app_version
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
            response = requests.get(self.server_url + '/version_info.json',
                    headers={'Content-Type': 'application/json'},
                    timeout=(self.conn_timeout, self.read_timeout))
            if response.status_code == 200:
                config = response.json()
                self.native.logi(config)
                if config.get('force', False) or compare_version(config['version'], self.app_version):
                    with open(DP.UPDATE_CONFIG_PATH, 'w') as fw:
                        fw.write(json.dumps(config, indent=4))
                    return config
                else:
                    self.native.logw(f'version: {self.app_version} vs {config["version"]}')
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
        if not zip_url.startswith('http'):
            zip_url = f'{self.server_url}/{update_config["url"]}'
        zip_md5 = update_config['md5']
        dst_dir = f'{DP.UPDATE_INSTALL_PATH}/{update_config["version"]}'
        tmp_dir = '/tmp/jetrep_update'
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
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            # 3. unzip
            self.native.logi('Unzip [%s]!' % DP.UPDATE_ZIP_PATH)
            subprocess.call(f'/usr/bin/unzip -qo {DP.UPDATE_ZIP_PATH} -d {tmp_dir}', shell=True)
            if update_config.get('compatible', True):
                self.native.logi(f'copy {DP.JETREP_CONF_PATH} to {tmp_dir}/{DP.APP_NAME}/{DP.RUNTIME_NAME}/')
                os.makedirs(f'{tmp_dir}/{DP.APP_NAME}/{DP.RUNTIME_NAME}/', exist_ok=True)
                shutil.copy(DP.JETREP_CONF_PATH, f'{tmp_dir}/{DP.APP_NAME}/{DP.RUNTIME_NAME}/')

            # 4. install(soft link)
            self.native.logi(f'make link[{dst_dir}/{DP.APP_NAME}]')
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.move(tmp_dir, dst_dir)
            os.remove(DP.UPDATE_ZIP_PATH)
            os.remove(DP.APP_LINK)
            os.symlink(f'{dst_dir}/{DP.APP_NAME}', DP.APP_LINK)

            # 5. notify message
            self.native.send_message(MessageType.UPGRADE, UpgradeType.OTA, PayloadType.UPGRADE_SUCCESS)

        except subprocess.CalledProcessError as exc:
            payload = f'Run subprocess: {exc.cmd} returncode: {exc.returncode}'
            self.native.send_message(MessageType.UPGRADE, UpgradeType.OTA, PayloadType.UPGRADE_ERROR, payload)
        except Exception as err:
            traceback.print_stack(limit=6)
            self.native.send_message(
                MessageType.UPGRADE,
                UpgradeType.OTA,
                PayloadType.UPGRADE_ERROR,
                f'{err}')
        finally:
            if os.path.exists(DP.UPDATE_ZIP_PATH):
                os.remove(DP.UPDATE_ZIP_PATH)
        self.native.logi('OtaUpgrade thread quit!')
