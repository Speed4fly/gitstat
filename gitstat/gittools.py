#!/usr/bin/python 

import datetime
import re

import click
from PyInquirer import prompt
from rich.console import Console

from . import *

console = Console()
result = {}
choices_dir = []
date = {}


@click.command()
@click.option("--target_dir", default='.', help='Folder to scan')
@click.option("--start_time", default=str(datetime.date.today() + datetime.timedelta(days=-365)),
              help='Date to end analyse, yyyy-mm-dd')
@click.option("--end_time",
              default=str(datetime.date.today()),
              help='Date to start analyse, yyyy-mm-dd',
              )
@click.option("--author",
              default=git('config', 'user.email'),
              help='Email of git',
              )
# @click.option("--author",  help = 'Email of git', required=True)
# @click.option

def cli(target_dir, start_time, end_time, author):
    target_dirs = scan(target_dir)
    console.print('User : ', author, style="bold red")
    # print(target_dirs)
    count = 0
    for target_dir in target_dirs:
        count_i = 0
        count_d = 0
        res = git('-C', target_dir, 'log', '--shortstat', '--author', author.strip(), '--since=' + start_time,
                            '--until=' + end_time)
        # 37 insertions(+), 90 deletions(-)
        # [0-9]+? insertions [0-9]+? deletions
        # click.echo(res)
        # print(res)
        insertions = re.findall(r'[0-9]+? insertions', res)
        print(res)
        date_raw = re.findall(r'Date:   [A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]+? [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}', res)
        # Date:   Wed Jan 6 10:22:28 2021 +0800
        print(date_raw)
        for date_raw_single in date_raw:
            date_stat(date, date_raw_single)

        for r in insertions:
            i = re.findall(r'[0-9]+', r)
            count_i += int(i[0])
        deletions = re.findall(r'[0-9]+? deletions', res)
        for r in deletions:
            i = re.findall(r'[0-9]+', r)
            count_d += int(i[0])
        if count_i != 0 or count_d != 0:
            temp_str_list = re.split(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', date_raw[0])

            result[target_dir] = [count_i, count_d, temp_str_list[0][7:] + temp_str_list[1]]
            choices_dir.append(target_dir)
        count = count + count_i + count_d

    if count == 0:
        console.print("no Repositoriy found!", style="bold yellow")
        return 0
    choices = []
    for item in choices_dir:
        choices.append({'name': item})
    questions = [
        {
            'type': 'checkbox',
            'qmark': ':)',
            'message': 'Select Repositories to analyse',
            'name': 'Repositories',
            'choices': choices,
            'validate': lambda answer: 'You must choose at least one Repository.' \
                if len(answer) == 0 else True
        }
    ]

    answers = prompt(questions)

    # print(type(answers))
    i = 0
    d = 0
    console.print("\nFrom ", start_time, " to ", end_time, " : ", style="bold yellow")

    for item in answers['Repositories']:
        i += result[item][0]
        d += result[item][1]
        date_stat(date, result[item][2])
        console.print("\nIn " + item + ' , the number of insertions is ', result[item][0],
                      ', the number of deletions is ', result[item][1], ' . ', style="bold white")
    # for item in answers[Repositories]:
    max_value = 0
    busy_day = 0
    for key, value in date.items():
        if value > max_value:
            max_value = value
            busy_day = key
    console.print("\nYou commit ", date[busy_day], 'times in ', busy_day, '. Such a busy day!', style="bold white")
    console.print("\nThe sum of insertions is ", i, " , the sum of deletions is ", d, " , total is ", i + d, ' . ',
                  style="bold red")



