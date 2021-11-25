#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file wifi.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-25 19:20


import re, os
import subprocess
import select
import random
import time
from multiprocessing import Process, Event
from jetrep.utils.net import util_get_uuid


def wifi_list():
    """
    nmcli dev wifi connect [essid] password [password]
    [   0         1      2       3       4       5         6        7        8]
    ['IN-USE', 'SSID', 'MODE', 'CHAN', 'RATE', 'SIGNAL', 'BARS', 'SECURITY', '']
    """
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


class WifiAP(Process):

    def __init__(self, **kwargs):
        super(WifiAP, self).__init__(name='wifiap')
        self.exit = Event()
        self.ssid = f'Jet-{util_get_uuid()[-6:]}'
        self.pswd = '12345678'
        self.chnl = random.randint(1, 11)

    def kill(self):
        self.exit.set()
        os.kill(self.pid, 9)

    def run(self):
        runner = subprocess.Popen(
            args=['/jetrep/bin/create_ap', '--country', 'CN', '-n', 'wlan0', self.ssid, self.pswd],
            encoding='utf8',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

        poll = select.poll()
        poll.register(runner.stdout, select.POLLIN)
        while not self.exit.is_set():
            if poll.poll(1):
                output = runner.stdout.readline()
                if output == '' and runner.poll() is not None:
                    for err in runner.stderr.readlines():
                        print('WifiAP Err: ', err)
                else:
                    print('WifiAP Out: ', output)
            time.sleep(0.5)


if __name__ == "__main__":
    print(wifi_list())
    print(wifi_status())
