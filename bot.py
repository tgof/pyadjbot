#!/usr/bin/python
# -- coding: utf-8 --
import config
import telebot
import socket
import threading
import datetime
import time
import sys
import traceback
import os


bot = telebot.TeleBot(config.token)
admin_id = 91531717
shell_enable = 0


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


def log(message):
    print(str(datetime.datetime.now()) + ' ' + message.from_user.first_name + ' ' + message.from_user.last_name + u'id:' + str(message.chat.id) + u' написал \"' + message.text + '\"')


@bot.message_handler(commands=['ssh'])
def command_answer(message):
    global shell_enable
    log(message)
    if message.from_user.id == admin_id:
        shell_enable ^= 1


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
            bot.send_message(message.chat.id, u'Ошибочка ' + str(exc_type) + ' ' + str(exc_value))
            traceback.print_tb(exc_traceback, limit=3, file=sys.stdout)


def main_loop():
    try:
        bot.polling(none_stop=True)
    except Exception:
        e = sys.exc_info()
        print(e)
        bot.stop_polling()
        return -1
    return 0


if __name__ == '__main__':
    statement = -1
    while statement == -1:
         statement = main_loop()

