# !/usr/bin/python


import os
import subprocess

__all__ = ['scan', 'git', 'date_stat', ]


def scan(target='.'):
    # flag = 1
    target_dirs = []
    for dirs in os.walk(target):
        for dir_names in dirs[1:]:
            for dir_name in dir_names:
                flag = 0
                if '.git' == dir_name:
                    for target_dir in target_dirs:
                        if dirs[0][:len(target_dir)] == target_dir:
                            flag = 1
                            break
                    if not flag:
                        target_dirs.append(dirs[0])
                        # self.flag = 0
                    continue

    return target_dirs


def git(*commands):
    try:
        out_bytes = subprocess.check_output(['git'] + list(commands))
        return out_bytes.decode('utf-8')
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        return out_bytes.decode('utf-8')


def date_stat(date, date_raw_single):
    if not date.__contains__(date_raw_single):
        date[date_raw_single] = 1
    else:
        date[date_raw_single] += 1
