#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file wifi.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-25 19:20


import re, os
import subprocess
import threading
import select
import random
import time
from multiprocessing import Lock
from jetrep.utils.net import util_get_uuid
from jetrep.constants import DefaultPath as DP


def wifi_list():
    """
    nmcli dev wifi connect [essid] password [password]
    [   0         1      2       3       4       5         6        7        8]
    ['IN-USE', 'SSID', 'MODE', 'CHAN', 'RATE', 'SIGNAL', 'BARS', 'SECURITY', '']
    """
    # fields = ['IN-USE', 'SSID', 'MODE', 'CHAN', 'RATE', 'SIGNAL', 'SECURITY']
    proc = subprocess.Popen("nmcli device wifi list", shell=True, stdout=subprocess.PIPE)
    wilist = []
    for i, line in enumerate(proc.stdout.readlines()):
        if i == 0:
            continue
        info = re.split(r"\s{2,}", line.decode())
        wilist.append({
            'IN-USE': True if info[0] else False,
            'SSID': info[1],
            'MODE': info[2],
            'CHAN': info[3],
            'RATE': info[4],
            'SIGNAL': info[5],
            'SECURITY': info[7]
        })
    return wilist


def wifi_status():
    """
    [   0        1       2          3 ]
    ['DEVICE', 'TYPE', 'STATE', 'CONNECTION', '']
    """
    proc = subprocess.Popen('nmcli device status', shell=True, stdout=subprocess.PIPE)
    wistatus = []
    for i, line in enumerate(proc.stdout.readlines()):
        if i == 0:
            continue
        info = re.split(r"\s{2,}", line.decode())
        if 'wifi' != info[1]:
            continue
        wistatus.append({
            'DEVICE': info[0],
            'STATE': info[2],
            'CONNECTION': info[3]
        })

    return wistatus


def wifi_active():
    """
    nmcli connection show --active
    [  0       1       2        3 ]
    ['NAME', 'UUID', 'TYPE', 'DEVICE']
    """
    proc = subprocess.Popen('nmcli connection show --active', shell=True, stdout=subprocess.PIPE)
    wiactive = []
    for i, line in enumerate(proc.stdout.readlines()):
        if i == 0:
            continue
        info = re.split(r"\s{2,}", line.decode())
        if 'wifi' != info[2]:
            continue
        wiactive.append({
            'NAME': info[0],
            'UUID': info[1],
            'DEVICE': info[3]
        })

    return wiactive


def wifi_connect(ssid, password):
    """
    storage wifi connection info:
        nmcli connection show
        nmcli connection up $ssid
    """
    result = subprocess.check_output(
            f'nmcli device wifi connect {ssid} password {password}',
            stderr=subprocess.STDOUT, shell=True).decode('utf-8').strip()
    print(result)
    if 'successfully' in result:
        return True
    return False


def wifi_disconnect(ssid):
    result = subprocess.check_output(
            f'nmcli device disconnect {ssid}',
            stderr=subprocess.STDOUT, shell=True).decode('utf-8').strip()
    print(result)
    return True


class WifiAP(threading.Thread):

    def __init__(self, logger, **kwargs):
        super(WifiAP, self).__init__(name='wifiap')
        self.logger = logger
        self.ssid = f'Jet-{util_get_uuid()[-6:]}'
        self.pswd = '12345678'
        self.device = 'wlan0'
        self.chnl = random.randint(1, 11)
        self.exit = False
        self.ap_proc = None
        self.lock = Lock()
        self.lock.acquire()
        super().start()

    def quit(self):
        self.exit = True
        self.stop()

    def stop(self):
        if self.ap_proc:
            self.ap_proc.kill()

    def start(self):
        self.lock.release()

    def ap_task(self):
        environment = os.environ.copy()
        environment['PATH'] = f'{DP.JETREP_BIN}:{environment["PATH"]}'
        self.logger.info(environment)
        runner = subprocess.Popen(
            args=['create_ap', '--country', 'CN', '-n', self.device, self.ssid, self.pswd],
            encoding='utf8',
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)
        self.ap_proc = runner
        poll = select.poll()
        poll.register(runner.stdout, select.POLLIN)
        while not self.exit:
            if poll.poll(1):
                output = runner.stdout.readline()
                if output == '' and runner.poll() is not None:
                    for err in runner.stderr.readlines():
                        self.logger.error(f'WifiAP Err: {err}')
                        raise
                else:
                    self.logger.info(f'WifiAP Out: {output}')
            time.sleep(0.5)
        self.ap_proc = None
        runner.wait(timeout=1)

    def run(self):
        self.logger.info('WifiAP Thread Running')
        try:
            while not self.exit:
                self.logger.info('WifiAP acquire lock')
                self.lock.acquire()
                self.ap_task()
        except Exception:
            pass
        self.logger.warning('WifiAP Thread Quit!!!')


if __name__ == "__main__":
    print(wifi_list())
    print(wifi_status())
