import telebot
from decouple import config


bot = telebot.TeleBot(config('TELEGRAM_TOKEN'))

@bot.message_handler(commands=['start'])
def greet(message):
  print(str(message.from_user.first_name) + " - " + str(message.from_user.id))
  bot.send_message(message.chat.id, f"Hey! {message.from_user.first_name} - {message.from_user.id} \nWelcome To The new Era-Telegram")

@bot.message_handler(commands=['tag'])
def send_welcome(message):
    bot.reply_to(message, "@727906232")


bot.infinity_polling()
