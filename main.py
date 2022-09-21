import telebot
from decouple import config


bot = telebot.TeleBot(config('TELEGRAM_TOKEN'))


@bot.message_handler(commands=['all'])
def start_message(message):
    bot.send_message(message.chat.id, '@FpsPerSecond')


bot.infinity_polling()
