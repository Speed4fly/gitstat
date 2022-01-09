# !/usr/bin/python


import os
import re
import subprocess

from rich.progress import track

__all__ = ['scan', 'git', 'date_stat', 'commit_is_code', 'pattern', 'lazy_scan']


def pattern(extra_name: str = None):
    codes = {
        'Vue': [
            'vue',
        ],  # Vue
        'Python': [
            'py',
        ],  # Python
        'C family': [
            'c',  # C family
            'h',
            'cpp',
            'hpp',
            'cc',
            'cs',
            'hxx',
            'cxx',
            'c\+\+',
            'm',
            'mm',
        ],
        'CoffeeScript': [
            'coffee',
        ],  # CoffeeScript
        'CSS': [
            'css',
        ],  # css
        'Html': [
            'html',  # html
            'htm',
        ],
        'Dart': [
            'dart',
        ],  # Dart
        'DM': [
            'dm',
        ],  # DM
        'Elixir': [
            'ex',  # Elixir
            'exs',
        ],
        'Go': [
            'go',
        ],  # Go
        'Groovy': [
            'groovy',
        ],  # Groovy
        'Java': [
            'java',
        ],  # Java
        'JavaScript': [
            'js',
        ],  # JavaScript
        'Kotlin': [
            'kt',
        ],  # Kotlin
        'Perl': [
            'pl',
        ],  # Perl
        'PHP': [
            'php',
        ],  # PHP
        'PowerShell': [
            'ps',
        ],  # PowerShell
        'Ruby': [
            'rb',
        ],  # Ruby
        'Rust': [
            'rs',
        ],  # Rust
        'Scala': [
            'scala',
        ],  # Scala
        'Shell': [
            'sh',
        ],  # Shell
        'Swift': [
            'swift',
        ],  # Swift
        'TypeScript': [
            'ts',
        ],  # TypeScript
    }
    patterns_ = {}
    if extra_name:
        codes['Custom'] = extra_name
    for code_name, code_list in codes.items():
        patterns_[code_name] = f".({'|'.join(code_list)})\n"
    return codes, patterns_


def scan(target='.') -> list:
    target_dirs = []
    dirs_ = list(os.walk(target))
    for dirs in track(dirs_, total=len(dirs_)):
        if os.path.isdir(f"{dirs[0]}/.git"):
            target_dirs.append(dirs[0])
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


def commit_is_code(commit, pattern_):
    if re.search(pattern_, commit, flags=re.IGNORECASE) is not None:
        return True
    return False


def lazy_scan(target: str) -> list:
    if os.path.isdir(f"{target}/.git"):
        return ['.']
    target_dirs = []
    dirs = os.listdir(target)
    for dir_ in track(dirs, total=len(dirs)):
        if os.path.isdir(f"{target}/{dir_}/.git"):
            target_dirs.append(f"{target}/{dir_}")
    return target_dirs
