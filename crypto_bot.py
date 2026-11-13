# pip install pyTelegramBotAPI requests
import requests
import telebot
from telebot import types

TOKEN = "9144536681:AAEcMOMtPT5OhupLwSg7J2ZZvQOyhQT6Fw0"

bot = telebot.TeleBot(TOKEN)

COINS = {
    "ton": ("Toncoin (TON)", "the-open-network"),
    "btc": ("Bitcoin (BTC)", "bitcoin"),
}


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Курс"))
    return kb


def coins_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("TON", callback_data="coin:ton"),
        types.InlineKeyboardButton("Bitcoin", callback_data="coin:btc"),
    )
    return kb


def get_rate(coin_id):
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": coin_id,
            "vs_currencies": "rub,usd",
            "include_24hr_change": "true",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()[coin_id]


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Нажми «Курс» и выбери монету.",
        reply_markup=main_keyboard(),
    )


@bot.message_handler(func=lambda m: m.text == "Курс")
def course(message):
    bot.send_message(message.chat.id, "Выбери криптовалюту:", reply_markup=coins_keyboard())


@bot.callback_query_handler(func=lambda c: c.data.startswith("coin:"))
def coin_chosen(call):
    key = call.data.split(":")[1]
    name, coin_id = COINS[key]
    try:
        d = get_rate(coin_id)
        change = d.get("rub_24h_change") or d.get("usd_24h_change") or 0
        text = (
            f"{name}\n"
            f"{d['rub']:,.2f} ₽\n"
            f"{d['usd']:,.2f} $\n"
            f"За 24 ч: {change:+.2f}%"
        )
    except Exception as e:
        text = f"Не получилось получить курс: {e}"
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)


bot.infinity_polling()
