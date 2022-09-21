# documentation https://core.telegram.org/bots/api
import telebot
from config import help_txt, keys, TOKEN # , admins
from extentions import APIException, CryptoConverter


bot = telebot.TeleBot(TOKEN)
print('starting with token:', TOKEN)


@bot.message_handler(commands=['start', 'help', 'помощь', 'справка', '?', 'h'])
def help(message: telebot.types.Message):
    bot.send_message(message.chat.id, f"Welcome, {message.chat.username}")
    bot.reply_to(message, help_txt)
    # print('started:', message.chat.id)


@bot.message_handler(commands=['values', 'валюты', 'v', 'в'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text += '\n - ' + key + ': ' + keys[key]
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        msgs = message.text.split(' ')
        # read arguments
        if type(msgs) != list or len(msgs) != 3:
            raise APIException('Неверное число аргументов')
        quote, base, amount = msgs

        # convert currency
        total_base = CryptoConverter.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя:\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду:\n{type(e)}: {e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)
