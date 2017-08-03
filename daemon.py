#!/usr/bin/python
# -- coding: utf-8 --
import os
import time

while True:
    ret = os.system('python bot.py')
    if int(ret) == 0:
        exit()
    time.sleep(1)