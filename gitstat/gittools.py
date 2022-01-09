#!/usr/bin/python

import datetime
import re

import click
from PyInquirer import prompt
from rich.console import Console
from rich.progress import track
from rich.table import Table

from . import *

console = Console()
result = {}
choices_dir = []
date = {}


@click.command()
@click.option("--ext_names",
              "-f",
              default=None,
              multiple=False,
              help='特殊的源代码文件扩展名,不包含点号,例如 txt ')
@click.option("--target_dir", "-t", default='.', help='要扫描的路径')
@click.option("--start_time",
              "-s",
              default=str(datetime.date.today() +
                          datetime.timedelta(days=-365)),
              help='结束统计的日期, yyyy-mm-dd')
@click.option(
    "--end_time",
    "-e",
    default=str(datetime.date.today()),
    help='开始统计的日期, yyyy-mm-dd',
)
@click.option(
    "--author",
    "-a",
    default=git('config', 'user.email')[:-1],
    help='Email of git',
)
@click.option(
    "--mode",
    "-m",
    default="lazy",
    help='搜索代码仓库的模式，默认为lazy模式（即仅搜索当前目录下一级），full模式会遍历所有子目录。'
)
def cli(target_dir, start_time, end_time, author, ext_names, mode):
    date_flag = 0
    table_flag = 0
    if mode == 'full':
        target_dirs = scan(target_dir)
    else:
        target_dirs = lazy_scan(target_dir)
    codes, patterns = pattern(ext_names)
    count = 0
    choices = []
    if not target_dirs:
        print("路径内无仓库.")
        return 0
    for item in target_dirs:
        choices.append({'name': item})
    questions = [
        {
            'type': 'checkbox',
            'qmark': ':)',
            'message': '选择要统计的仓库目录,<a>全选,<i>反选,方向键移动,空格选择.',
            'name': 'Repositories',
            'choices': choices,
            'validate': lambda answer: '请至少选择一个仓库.' \
                if len(answer) == 0 else True
        }
    ]

    answers = prompt(questions)
    sum_i = 0
    sum_d = 0

    table = Table(show_header=True, header_style="bold green")
    table.add_column("仓库")
    table.add_column("分支")
    table.add_column("新增", justify="right")
    table.add_column("移除", justify="right")
    table.add_column("共计", justify="right")

    table_code = Table(show_header=True, header_style="bold green")
    table_code.add_column("语言")
    table_code.add_column("新增", justify="right")
    table_code.add_column("移除", justify="right")
    table_code.add_column("共计", justify="right")

    for item in track(answers['Repositories']):
        result[item] = {}
        count_i = 0
        count_d = 0
        head = git('-C', item, 'symbolic-ref', '--short', '-q', 'HEAD')[:-1]
        res = git('-C', item, 'log', head, '--numstat', '--author', author,
                  '--since=' + start_time, '--until=' + end_time)

        insertions_and_deletions = re.findall(
            r'[0-9]+?\t[0-9]+?\t(?!\+).+?\.+?.+?\n', res)

        for code_name in codes.keys():
            result[item][code_name] = [0, 0]

        for strings in insertions_and_deletions:
            for code_name in codes.keys():
                if commit_is_code(strings, patterns[code_name]):
                    str_tmp = re.findall(r'[0-9]+?\t', strings)
                    result[item][code_name][0] += int(str_tmp[0][:-1])
                    result[item][code_name][1] += int(str_tmp[1][:-1])
                    # insertions_and_deletions.remove(strings)

        date_raw = re.findall(
            r'Date: {3}[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]+? [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}',
            res)
        for i in date_raw:
            temp_str_list = re.split(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', i)
            tmp_date = temp_str_list[0][7:] + temp_str_list[1]
            date_stat(date, tmp_date)
            date_flag = 1

        for values in result[item].values():
            count_i += values[0]
            count_d += values[1]
        if (count_i + count_d) != 0:
            table.add_row(
                item, head, str(count_i), str(count_d),
                '[cyan][bold]' + str(count_i + count_d) + '[/bold][/cyan]')
            count = count + count_i + count_d
            sum_i += count_i
            sum_d += count_d
            table_flag = 1

    count_code = {}
    for code_name in codes:
        count_code[code_name] = [0, 0]
        for item in answers['Repositories']:
            count_code[code_name][0] += result[item][code_name][0]
            count_code[code_name][1] += result[item][code_name][1]
        if (count_code[code_name][0] + count_code[code_name][1] !=
            0) | (code_name == 'Custom'):
            table_code.add_row(
                code_name, str(count_code[code_name][0]),
                str(count_code[code_name][1]), '[bold]' +
                                               str(count_code[code_name][0] + count_code[code_name][1]) +
                                               '[/bold]')

    table.add_row("[red]总计[/red]",
                  '/',
                  str(sum_i),
                  str(sum_d),
                  str(sum_i + sum_d),
                  style='bold cyan')
    console.print("\n自", start_time, "至", end_time, ":", style="bold")
    console.print('账户:', author, style="bold red")
    if table_flag:
        console.print(table)
        console.print(table_code)
    else:
        print("所选仓库中无代码提交.")
        return 0

    if date_flag:
        max_value = 0
        busy_day = 0
        for key, value in date.items():
            if value > max_value:
                max_value = value
                busy_day = key
        console.print("\n在 ",
                      busy_day,
                      '这一天,你提交了 ',
                      date[busy_day],
                      ' 次. ',
                      style="bold white")
