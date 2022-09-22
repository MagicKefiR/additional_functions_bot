import telebot
from decouple import config
import sys
from getpass import getpass
from time import sleep
# pip install telethon==0.11.5
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpc_errors_400 import UsernameNotOccupiedError
from telethon.errors.rpc_errors_420 import FloodWaitError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import ChannelParticipantsSearch, InputChannel


bot = telebot.TeleBot(config('TELEGRAM_TOKEN'))

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(message.chat.id,
                     f"Здравствуй! Я бот текстовых команд.\nНапиши /all, чтобы отметить всех пользователей.")

@bot.message_handler(commands=['all'])
def send_answer(message):
    tags = bot.chat
    bot.send_message(message.chat.id, tags)

def authorization():
    # запрашиваем чат
    channel_name = input('Input a channel name, without "@": ')
    client = TelegramClient('current-session', config(API_ID), config(API_HASH))
    client.connect()
    # проверяем не залогинены ли вы уже
    # как можно видеть выше мы создали сессию под именем current-session
    # после первой авторизации можно будет использовать её
    if not client.is_user_authorized():
        try:
            # отсылаем код подтверждения
            client.send_code_request(config(PHONE))
            client.sign_in(config(PHONE), code=input('Enter code: '))
        # иногда телеграмм блокирует доступ на +- 80к сек
        # так что будьте аккуратны и не посылайте слишком много запросов
        except FloodWaitError as FloodError:
            print('Flood wait: {}.'.format(FloodError))
            sys.exit()
        # проверяем есть ли у пользователя пароль
        # если да, запрашиваем его и логинимся
        except SessionPasswordNeededError:
            client.sign_in(password=getpass('Enter password: '))
    # об этой функции расскажу ниже
    dump_users(get_chat_info(channel_name, client), client)

def get_chat_info(username, client):
    try:
        chat = client(ResolveUsernameRequest(username))
    except UsernameNotOccupiedError:
        print('Chat/channel not found!')
        sys.exit()
    result = {
        'chat_id': chat.peer.channel_id,
        'access_hash': chat.chats[0].access_hash
    }
    return result

def dump_users(chat, client):
    counter = 0
    offset = 0
    # нам нужно сделать объект чата, как сказано в документации
    chat_object = InputChannel(chat['chat_id'], chat['access_hash'])
    all_participants = []
    while True:
        # тут мы получаем пользователей
        # всех сразу мы получить не можем для этого нам и нужен offset
        participants = client.invoke(GetParticipantsRequest(
                    chat_object, ChannelParticipantsSearch(''), offset, limit
                ))
        # если пользователей не осталось, т.е мы собрали всех, выходим
        if not participants.users:
            break
        all_participants.extend(['{} {}'.format(x.id, x.username)
                           for x in participants.users])
        users_count = len(participants.users)
        # увеличиваем offset на то кол-во юзеров которое мы собрали
        offset += users_count
        counter += users_count
        print('{} users collected'.format(counter))
        # не забываем делать задержку во избежания блокировки
        sleep(2)
    # сохраняем в файл
    with open('users.txt', 'w') as file:
        file.write('\n'.join(map(str, all_participants)))

bot.infinity_polling()
