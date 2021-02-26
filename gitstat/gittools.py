#!/usr/bin/python 

import datetime
import re
import time

import click
from PyInquirer import prompt
from rich.console import Console
from rich.progress import track
from rich.table import Table, Column

from . import *

console = Console()
result = {}
choices_dir = []
date = {}


@click.command()
@click.option("--target_dir", "-t", default='.', help='Folder to scan')
@click.option("--start_time", "-s", default=str(datetime.date.today() + datetime.timedelta(days=-365)),
              help='Date to end analyse, yyyy-mm-dd')
@click.option("--end_time", "-e",
              default=str(datetime.date.today()),
              help='Date to start analyse, yyyy-mm-dd',
              )
@click.option("--author", "-a",
              default=git('config', 'user.email'),
              help='Email of git',
              )
# @click.option("--author",  help = 'Email of git', required=True)
# @click.option

def cli(target_dir, start_time, end_time, author):
    target_dirs = scan(target_dir)
    # console.print('User : ', author, style="bold red")
    # print(target_dirs)
    count = 0
    choices = []
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

    for item in track(answers['Repositories']):

        count_i = 0
        count_d = 0
        head = git('-C', item, 'symbolic-ref', '--short', '-q', 'HEAD').strip()
        res = git('-C', item, 'log', head, '--shortstat', '--author', author.strip(), '--since=' + start_time,
                  '--until=' + end_time)
        # 37 insertions(+), 90 deletions(-)
        # [0-9]+? insertions [0-9]+? deletions
        # click.echo(res)
        # print(res)

        insertions = re.findall(r'[0-9]+? insertions', res)
        date_raw = re.findall(r'Date:   [A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]+? [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}',
                              res)
        # Date:   Wed Jan 6 10:22:28 2021 +0800
        # print(date_raw)
        # for date_raw_single in date_raw:
        #     date_stat(date, date_raw_single)

        for r in insertions:
            i = re.findall(r'[0-9]+', r)
            count_i += int(i[0])
        deletions = re.findall(r'[0-9]+? deletions', res)
        for r in deletions:
            i = re.findall(r'[0-9]+', r)
            count_d += int(i[0])
        for i in date_raw:
            temp_str_list = re.split(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', i)
            tmp_date = temp_str_list[0][7:] + temp_str_list[1]
            date_stat(date, tmp_date)
            # result[item] = [count_i, count_d, tmp_date]
            # choices_dir.append(target_dir)
        table.add_row(item, head, str(count_i), str(count_d),
                      '[cyan]' + str(count_i + count_d) + '[/cyan]', style='bold')
        count = count + count_i + count_d
        sum_i += count_i
        sum_d += count_d

    if count == 0:
        console.print("找不到有提交的仓库.", style="bold yellow")
        return 0

    # print(date)
    # i += result[item][0]
    # d += result[item][1]
    table.add_row("[red]总计[/red]", '/', str(sum_i), str(sum_d), '[red]' + str(sum_i + sum_d) + '[/red]', style='cyan')
    console.print("\n自 ", start_time, " 至 ", end_time, " : ", style="bold yellow")
    console.print('账户:', author, style="bold red")
    console.print(table)

    # for item in answers[Repositories]:
    max_value = 0
    busy_day = 0
    for key, value in date.items():
        if value > max_value:
            max_value = value
            busy_day = key
    console.print("\n在 ", busy_day, '这一天,你提交了 ', date[busy_day], ' 次. ', style="bold white")
