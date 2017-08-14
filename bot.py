#!/usr/bin/python
# -- coding: utf-8 --
import config
import telebot
import socket
import datetime
import time
import sys
import traceback
import os
import threading


bot = telebot.TeleBot(config.token)
admin_id = config.admin_id
shell_enable = 0
log_lock = threading.Lock()


def my_server():
    sock = socket.socket()
    sock.bind(('', 9001))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        print ('connected: ' + str(addr))
        data = conn.recv(1024)
        if not data:
            break
        bot.send_message(admin_id, data)
        time.sleep(1)
        conn.close()


my_func_thread = threading.Thread(target=my_server)
my_func_thread.daemon = True
my_func_thread.start()


def log(message=None, error=None):
    if message is not None:
        user = message.from_user
        first_name = user.first_name
        if first_name is None:
            first_name = 'None'
        first_name = first_name.encode('utf-8').decode('utf-8')
        last_name = user.last_name
        if last_name is None:
            last_name = 'None'
        last_name = last_name.encode('utf-8').decode('utf-8')
        line = str(datetime.datetime.now()) + ' ' + first_name + ' ' + last_name + u' id:'\
            + str(user.id) +u' в чат id: ' + str(message.chat.id) + u' написал \"' + message.text + '\"\n'
    elif error is not None:
        line = str(datetime.datetime.now()) + ' ' + error + '\n'
    else:
        line = str(datetime.datetime.now()) + ' log with empty params'
    line = line.encode('utf8')
    log_lock.acquire()
    f = open('log.txt', 'a')
    f.write(line)
    f.close()
    log_lock.release()


def quiting():
    bot.stop_polling()
    print(str(datetime.datetime.now()) + ' Poling stoped')


@bot.message_handler(commands=['ssh'])
def command_answer(message):
    global shell_enable
    log(message)
    if message.from_user.id == admin_id:
        shell_enable ^= 1


@bot.message_handler(commands=['exit'])
def command_answer(message):
    log(message)
    if message.from_user.id == admin_id:
        bot.send_message(message.chat.id, u'Выключаюсь')
        quiting()
        sys.exit(0)


@bot.message_handler(commands=[u'пошёл_вон'])
def command_answer(message):
    log(message)
    bot.send_message(message.chat.id, u'Сам ты пошёл')
    if message.from_user.id == admin_id and str(message.chat.type) != 'private':
        bot.leave_chat(message.chat.id)


@bot.message_handler(commands=['gull'])
def command_answer(message):
    log(message)
    if message.from_user.id == admin_id:
        ret = os.popen('git pull').read()
        bot.send_message(message.chat.id, ret)
        if ret != 'Already up-to-date.':
            quiting()
            sys.exit(1)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    log(message)
    if shell_enable == 1 and message.from_user.id == admin_id:
        try:
            f = os.popen(message.text)
            res = f.read()
            if str(res) != '':
                bot.send_message(message.chat.id, str(res))
            else:
                bot.send_message(message.chat.id, u'Команда вернула пустую строку')
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log(error=str(exc_type) + ' ' + str(exc_value))
            bot.send_message(message.chat.id, u'Ошибочка ' + str(exc_type) + ' ' + str(exc_value))
            traceback.print_tb(exc_traceback, limit=3, file=sys.stdout)


def main_loop():
    try:
        print(str(datetime.datetime.now()) + ' Poling starting')
        bot._TeleBot__skip_updates()
        bot.polling(none_stop=True)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log(error=str(exc_type) + ' ' + str(exc_value))
        bot.send_message(admin_id, 'Я в беде!')
        quiting()
        return -1
    return 0


if __name__ == '__main__':
    ret = main_loop()
    sys.exit(-1)

