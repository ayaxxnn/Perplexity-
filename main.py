import telebot
from flask import Flask
from config import BOT_TOKEN, ADMIN_IDS
from utils import generate_key, load_data, save_data

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# START COMMAND
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Welcome To The Bot ⚡️\nPlease Use this /redeem Command For Get Prime video 🧑‍💻\nFor Premium use This Command /premium")

# GEN KEY (Admin Only)
@bot.message_handler(commands=['genk'])
def gen_key_cmd(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        days = int(message.text.split(" ")[1])
        key = generate_key(days)
        bot.reply_to(message, f"✅ Key Generated: <code>{key}</code>\nDays: {days}")
    except:
        bot.reply_to(message, "Usage: /genk <days>")

# PREMIUM REDEEM
@bot.message_handler(commands=['premium'])
def premium_cmd(message):
    key_parts = message.text.split(" ")
    if len(key_parts) < 2:
        bot.reply_to(message, "Please enter your key: /premium <key>")
        return

    key = key_parts[1].strip()
    data = load_data()

    if key in data["premium_keys"]:
        if message.from_user.id in data["premium_users"]:
            bot.reply_to(message, "You already have Premium!")
            return

        days = data["premium_keys"].pop(key)
        data["premium_users"][message.from_user.id] = {"days": days}
        save_data(data)

        bot.reply_to(message, "Premium Activated ⚡️")
        for admin in ADMIN_IDS:
            bot.send_message(admin, f"👑 Premium Activated by @{message.from_user.username or message.from_user.id}")
    else:
        bot.reply_to(message, "❌ Invalid Key!")

# REDEEM FEATURE (free or premium)
@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    data = load_data()
    uid = str(message.from_user.id)

    if message.from_user.id in data["premium_users"]:
        bot.reply_to(message, "Processing your redeem request ⚡️")
        for admin in ADMIN_IDS:
            bot.forward_message(admin, message.chat.id, message.message_id)
        return

    if data.get("free_service", False) or uid not in data["redeemed_users"]:
        data["redeemed_users"][uid] = True
        save_data(data)
        bot.reply_to(message, "Processing your redeem request ⚡️")
        for admin in ADMIN_IDS:
            bot.forward_message(admin, message.chat.id, message.message_id)
    else:
        bot.reply_to(message, "Please Purchase Premium Key For Use 🗝️")

# BROADCAST (Admin only)
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = message.text.replace("/broadcast ", "").strip()
    data = load_data()
    for user_id in set(list(data["redeemed_users"].keys()) + list(data["premium_users"].keys())):
        try:
            bot.send_message(user_id, text)
        except:
            pass

# ON/OFF FREE SERVICE
@bot.message_handler(commands=['on'])
def on_cmd(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    data = load_data()
    data["free_service"] = True
    save_data(data)
    bot.reply_to(message, "Free Service On time ⚡️")
    for user in data["redeemed_users"].keys():
        bot.send_message(user, "Free Service On time ⚡️")

@bot.message_handler(commands=['off'])
def off_cmd(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    data = load_data()
    data["free_service"] = False
    save_data(data)
    bot.reply_to(message, "Free Service Off ♻️")
    for user in data["redeemed_users"].keys():
        bot.send_message(user, "Free Service Off ♻️")

import threading

def run_telebot():
    bot.infinity_polling()

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_telebot).start()
    run_flask()
