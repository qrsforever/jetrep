#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file shell.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 11:09

import subprocess
import psutil


def util_check_service(sname):
    try:
        # MainPID
        # status = subprocess.check_output(f'systemctl show -p ActiveState --value {sname}', shell=True)
        status = subprocess.check_output(f'systemctl is-active {sname}', shell=True)
        if status.decode('utf-8').strip() == 'active':
            return True
    except Exception:
        return False
    return False


def util_start_service(sname, restart=False):
    try:
        result = subprocess.call(['systemctl', 'restart' if restart else 'start', sname])
        return result.returncode
    except Exception:
        return -1
    return -1


def util_stop_service(sname):
    try:
        result = subprocess.call(['systemctl', 'stop', sname])
        return result.returncode
    except Exception:
        return -1
    return -1


def util_get_pids(proname=None, keystr=None):
    if proname:
        try:
            return list(map(int, subprocess.check_output(["pidof", proname]).split()))
        except Exception:
            return []
    if keystr:
        pids = []
        for proc in psutil.process_iter():
            if keystr in ' '.join(proc.cmdline()):
                pids.append(proc.pid)
        return pids


def util_kill_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
    return gone, alive
