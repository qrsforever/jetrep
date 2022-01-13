#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file net.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 15:12

import os
import socket
import struct
import fcntl
import time
import uuid
import random
import subprocess
import ssl
from urllib import request, parse

ssl._create_default_https_context = ssl._create_unverified_context


def util_check_port(port, ip='127.0.0.1', trycnt=1):
    used = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for _ in range(trycnt):
            code = s.connect_ex((ip, port))
            if code == 0:
                used = True
            time.sleep(1)
    finally:
        s.close()
    return used


def util_get_ip(ifname='eth0'):
    val = '0.0.0.0'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        val = socket.inet_ntoa(
                fcntl.ioctl(
                    s.fileno(),
                    0x8915,
                    struct.pack('256s', bytes(ifname[:15], 'utf-8')))[20:24])
    except Exception:
        pass
    finally:
        s.close()
    return val


def util_get_mac(ifname='eth0'):
    # try:
    #     with open(f'/sys/class/net/{device}/address', 'r') as fr:
    #         mac = fr.readline().strip().replace(':', '')
    # except Exception:
    #     mac = "000000000000"
    # return mac
    val = '000000000000'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        val = fcntl.ioctl(
                s.fileno(),
                0x8927,
                struct.pack('256s', bytes(ifname[:15], 'utf-8')))[18:24]
        val = ''.join(['%02x' % b for b in val])
    except Exception:
        pass
    finally:
        s.close()
    return val


def util_get_lanip():
    val = '0.0.0.0'
    # try:
    #     # ret = socket.gethostbyname(socket.getfqdn(socket.gethostname())) # slow
    #     ret = socket.gethostbyname(socket.gethostname())
    # except Exception:
    #     pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        val = s.getsockname()[0]
    finally:
        s.close()
    return val


def util_get_netip():
    val = '0.0.0.0'
    try:
        result = os.popen('curl -s http://txt.go.sohu.com/ip/soip| grep -P -o -i "(\d+\.\d+.\d+.\d+)"', 'r') # noqa
        if result:
            val = result.read().strip('\n')
    except Exception:
        pass
    return val


def util_ping_request(hosts=('8.8.8.8', '1.1.1.1'), port=53, timeout=3):
    def_timeout = socket.getdefaulttimeout()
    val = False
    socket.setdefaulttimeout(timeout)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(3):
        try:
            s.connect((random.choice(hosts), port))
            val = True
            break
        except Exception:
            pass
    s.close()
    socket.setdefaulttimeout(def_timeout)
    return val


def util_send_broadcast(msg, port=1665):
    val = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, ('255.255.255.255', port))
        val = True
    finally:
        s.close()
    return val


## wifi ap

def _wifi_status(ssid='jethotspot', device='wlan0', is_active=False):
    try:
        proc = subprocess.Popen(
            'nmcli -t -f NAME,DEVICE connection show %s' % ('--active' if is_active else ''),
            stdout=subprocess.PIPE, shell=True)
        for line in proc.stdout.readlines():
            line = line.decode('utf-8').strip()
            if ssid in line or device in line:
                return True
    except Exception:
        pass
    return False


def _wifi_disconnect(device='wlan0'):
    try:
        if _wifi_status(device=device, is_active=True):
            output = subprocess.check_output(f'nmcli device disconnect {device}', shell=True)
            if 'successfully disconnected' in output.decode('utf-8').strip():
                time.sleep(3)
                return 0
        return 0
    except subprocess.CalledProcessError as err:
        return err.returncode
    except Exception:
        pass
    return -1


def _wifi_connect(device='wlan0'):
    try:
        output = subprocess.check_output(f'nmcli device connect {device}', shell=True)
        if 'successfully activated' in output.decode('utf-8').strip():
            return 0
    except subprocess.CalledProcessError as err:
        return err.returncode
    except Exception:
        pass
    return -1


def _wifi_delete_connection(ssid='jethotspot'):
    try:
        _wifi_disconnect()
        if _wifi_status(ssid=ssid):
            output = subprocess.check_output(f'nmcli connection delete {ssid}', shell=True)
            if 'successfully deleted' in output.decode('utf-8').strip():
                return 0
        return 0
    except subprocess.CalledProcessError as err:
        return err.returncode
    except Exception:
        pass
    return -1


def _wifi_rescan():
    try:
        subprocess.check_call(f'nmcli device wifi rescan', shell=True)
        return 0
    except subprocess.CalledProcessError as err:
        if 1 == err.returncode: # already scan
            time.sleep(3)
        return err.returncode
    except Exception:
        pass
    return -1


def util_create_hotspot(ssid='jethotspot', passwd='88888888', device='wlan0'):
    try:
        _wifi_delete_connection(ssid=ssid)
        output = subprocess.check_output(
            'nmcli connection add type wifi ifname {} con-name {} autoconnect no ssid {} ip4 {}'.format(
                device, ssid, ssid, '192.168.45.1/24'),
            shell=True)
        if 'successfully added' in output.decode('utf-8').strip():
            subprocess.check_call(
                f'nmcli connection modify {ssid} 802-11-wireless.mode ap ipv4.method shared',
                shell=True)
            subprocess.check_call(
                f'nmcli connection modify {ssid} wifi-sec.key-mgmt wpa-psk wifi-sec.psk {passwd}',
                shell=True)
            output = subprocess.check_output(f'nmcli connection up id {ssid}', shell=True)
            if 'successfully activated' in output.decode('utf-8').strip():
                return 0
    except subprocess.CalledProcessError as err:
        time.sleep(2)
        return err.returncode
    except Exception:
        pass
    return -1


def util_destroy_hotspot(ssid='jethotspot'):
    _wifi_disconnect()
    return _wifi_delete_connection(ssid=ssid)


def util_wifi_connect(ssid, passwd, apname, device='wlan0'):
    try:
        _wifi_disconnect()
        _wifi_delete_connection(ssid=apname)
        _wifi_delete_connection(ssid=ssid)
        _wifi_connect()
        _wifi_rescan()
        output = subprocess.check_output(
            f'nmcli device wifi connect {ssid} password {passwd}',
            shell=True)
        if 'successfully activated' in output.decode('utf-8').strip():
            return 0
    except subprocess.CalledProcessError as err:
        return err.returncode
    except Exception:
        pass
    return -1


def util_get_uuid():
    return uuid.uuid1().hex[-12:]


def util_request_data(x, path='/tmp'):
    if x.startswith('http') or x.startswith('ftp'):
        x = parse.quote(x, safe=':/?-=')
        if os.path.isdir(path):
            path = os.path.join(path, os.path.basename(x))
        r = request.urlretrieve(x, path)
        x = r[0]
    elif x.startswith('oss://'):
        raise NotImplementedError('weight schema: oss')
    elif x.startswith('file://'):
        x = x[7:]
    return x


if __name__ == "__main__":
    # print(_wifi_disconnect())
    # print(_wifi_delete_connection())
    # print(util_create_hotspot())
    # print(util_wifi_connect(ssid='国电社区', passwd='88888888', apname='JET-5bcfa5'))
    print(util_get_ip('xwlp4s0'))
    print(util_get_mac('xenp2s0'))
