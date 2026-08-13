import json
import os
import telebot
from telebot import types

TOKEN = '8932825989:AAHYteWAIY7QhQuM235m47nonTgXOgftv0c'
ADMIN_ID = 8849429887

bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'users.json'

try:
    bot.remove_webhook()
except Exception:
    pass

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

user_db = load_data()

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("👤 প্রোফাইল"), types.KeyboardButton("🔗 রেফার লিঙ্ক"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    name = message.from_user.first_name
    text_args = message.text.split()

    if user_id not in user_db:
        referrer_id = text_args[1] if len(text_args) > 1 and text_args[1] != user_id else None
        user_db[user_id] = {"name": name, "balance": 0, "refers": 0, "referred_by": referrer_id}

        if referrer_id and referrer_id in user_db:
            user_db[referrer_id]["balance"] += 10
            user_db[referrer_id]["refers"] += 1
            try:
                bot.send_message(int(referrer_id), f"🎉 নতুন রেফার! {name} জয়েন করেছে। ১০ টাকা যোগ করা হয়েছে।")
            except Exception:
                pass
        save_data(user_db)

    bot.send_message(message.chat.id, f"হ্যালো {name}! বটের ড্যাশবোর্ডে আপনাকে স্বাগতম।", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "👤 প্রোফাইল")
def show_profile(message):
    user_id = str(message.chat.id)
    if user_id not in user_db:
        user_db[user_id] = {"name": message.from_user.first_name, "balance": 0, "refers": 0, "referred_by": None}
        save_data(user_db)

    u = user_db[user_id]
    profile_text = f"👤 আপনার প্রোফাইল:\n\n🆔 ইউজার আইডি: `{user_id}`\n👤 নাম: {u['name']}\n💰 মোট ব্যালেন্স: {u['balance']} টাকা\n👥 মোট রেফার: {u['refers']} জন"
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔗 রেফার লিঙ্ক")
def ref_link(message):
    user_id = str(message.chat.id)
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start={user_id}"
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিঙ্ক:\n`{link}`", parse_mode="Markdown")

@bot.message_handler(commands=['add'])
def add_money(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "❌ আপনি অ্যাডমিন নন!")
        return
    try:
        args = message.text.split()
        target_user_id = str(args[1])
        amount = float(args[2])

        if target_user_id in user_db:
            user_db[target_user_id]["balance"] += amount
            save_data(user_db)
            bot.reply_to(message, f"✅ সফল হয়েছে!\nআইডি `{target_user_id}`-এ {amount} টাকা যোগ হয়েছে।\nনতুন ব্যালেন্স: {user_db[target_user_id]['balance']} টাকা", parse_mode="Markdown")
            try:
                bot.send_message(int(target_user_id), f"🎉 অভিনন্দন!\nঅ্যাডমিন আপনার অ্যাকাউন্টে {amount} টাকা পাঠিয়েছেন।\nবর্তমান ব্যালেন্স: {user_db[target_user_id]['balance']} টাকা")
            except Exception:
                pass
        else:
            bot.reply_to(message, "❌ ইউজার আইডি পাওয়া যায়নি।")
    except Exception:
        bot.reply_to(message, "⚠️ ব্যবহারের নিয়ম:\n`/add ইউজার_আইডি টাকা`\nউদাহরণ: `/add 123456789 20`", parse_mode="Markdown")

print("বট সফলভাবে চালু হয়েছে...")
bot.polling(none_stop=True)
