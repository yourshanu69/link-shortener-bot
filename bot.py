print("Script started")
import os
import random
from threading import Thread
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Shanu's Magic Bot is Alive! 🔥"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
PREMIUM_USERS = [1692907487]

tools_prompt = {
    'Banner Creator': "শুরু হচ্ছে...",
    'FF Diamond': "🎮 UID দাও",
    'Fake News': "📰 Headline লিখো",
    'Eid Rules': "দেখাচ্ছি...",
    'Bank Balance SS': "🏦 Amount লিখো",
    'Eid Greeting': "কার জন্য বানাবা? নাম লিখো",
    'Fun Zone': "খুলছে...",
    'Love ক্যালকুলেটর': "❤️ নাম1, নাম2 লিখো",
    'Roast': "🔥 কাকে roast করবা?",
    'Beauty Meter': "💎 ছবি পাঠাও, স্কোর দেব",
    'ভাগ্য গণনা': "🎲 তোমার নাম লিখো",
    'Fake Payment': "💰 Amount লিখো",
    'Image→PDF': "📷 ছবি পাঠাও",
    'Sticker': "🖼️ ছবি পাঠাও",
    'Remove BG': "🗑️ ছবি পাঠাও",
    'Text→PDF': "📝 Text লিখো",
    'PDF→Text': "📄 PDF পাঠাও",
    'Fake Chat': "💬 নাম1, নাম2 লিখো",
    'Stylish Font': "🔤 Text লিখো",
    'YouTube Thumbnail': "🎬 Title লিখো",
    'TTS': "🗣️ Text লিখো",
    'Deep Link': "🔗 লিংক পাঠাও"
}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = list(tools_prompt.keys())
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    
    bot.send_message(chat_id, "🔥 **22টা টুল রেডি** 😎\nনিচ থেকে যেকোনো একটা সিলেক্ট করো 👇",
                     reply_markup=markup, parse_mode="Markdown")
    user_state[chat_id] = None

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document'])
def handle_all(message):
    chat_id = message.chat.id
    text = message.text if message.text else ""
    state = user_state.get(chat_id, None)

    # FIX: কোনো টুল চলার মাঝে অন্য টুল চাপলে আগেরটা ক্যান্সেল হবে
    if state and text in tools_prompt and text!= 'Banner Creator':
        user_state[chat_id] = None
        bot.send_message(chat_id, "আগের প্রসেস ক্যান্সেল হলো ✅")

    # Banner এর শেষ স্টেপ হ্যান্ডেল
    if handle_banner_state(message, state, chat_id, text):
        return

    if text in tools_prompt:
        user_state[chat_id] = f"wait_{text}"
        bot.send_message(chat_id, tools_prompt[text])

        # 4টা ফুল টুল
        if text == 'Banner Creator':
            banner_start(message)
        elif text == 'Eid Rules':
            eid_rules(message)
        elif text == 'Fun Zone':
            fun_zone(message)
        elif text == 'Eid Greeting':
            eid_greeting(message)
        else:
            # বাকি 18টার ডেমো রেসপন্স
            user_state[chat_id] = None
            run_fake_logic(message, text)
    else:
        bot.send_message(chat_id, "মেনু থেকে একটা অপশন সিলেক্ট করো 👇")

def run_fake_logic(message, tool):
    txt = message.text
    responses = {
        'Roast': f"{txt} কে roast: তুমি WiFi ছাড়া Google এর মতো 😂",
        'Beauty Meter': f"💎 Beauty Score: {random.randint(70, 99)}%",
        'ভাগ্য গণনা': random.choice(["আজ টাকা পাবে", "ভালো খবর আসবে"]),
        'Love ক্যালকুলেটর': f"❤️ Love: {random.randint(60, 99)}% মিল আছে",
        'Fake Payment': f"✅ {txt}৳ Payment Successful! Fake 😎",
        'FF Diamond': f"✅ UID {txt} এ 500 Diamond পাঠানো হলো! Fake 😎",
        'Fake News': f"BREAKING: {txt} - সোর্স: ফেসবুক ইউনিভার্সিটি",
        'Bank Balance SS': f"✅ Balance: {txt}৳\nFake SS বানানো হলো"
    }
    msg = responses.get(tool, f"✅ {tool} কমপ্লিট! এটা ডেমো ভার্সন")
    bot.send_message(message.chat.id, msg)

# ====== Banner Creator ======
@bot.message_handler(func=lambda m: m.text == 'Banner Creator')
def banner_start(message):
    chat_id = message.chat.id
    is_premium = message.from_user.id in PREMIUM_USERS
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(f"T{i}", callback_data=f"tpl_eid_{i}") for i in range(1, 13)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ বাতিল", callback_data="tpl_cancel"))
    bot.send_message(chat_id, f"{'✨ Premium' if is_premium else '🆓 Free'}\n12টা টেমপ্লেট:", reply_markup=markup)
    user_state[chat_id] = 'banner_tpl'

@bot.callback_query_handler(func=lambda call: call.data.startswith('tpl_'))
def banner_tpl_select(call):
    chat_id = call.message.chat.id
    if call.data == 'tpl_cancel':
        bot.edit_message_text("বাতিল", chat_id, call.message.id)
        user_state[chat_id] = None
        return
    user_state[chat_id] = 'banner_photo'
    bot.edit_message_text("✅ টেমপ্লেট সিলেক্ট হলো\n1️⃣ ছবি পাঠাও", chat_id, call.message.id)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'banner_photo', content_types=['photo'])
def banner_photo(message):
    user_state[message.chat.id] = 'banner_name'
    bot.send_message(message.chat.id, "2️⃣ নাম লিখো:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'banner_name')
def banner_name(message):
    user_state[message.chat.id] = 'banner_addr'
    bot.send_message(message.chat.id, "3️⃣ ঠিকানা লিখো:")

def handle_banner_state(message, state, chat_id, text):
    if state == 'banner_addr':
        bot.send_message(chat_id, "✅ ব্যানার রেডি! Premium না হলে ওয়াটারমার্ক থাকবে।")
        user_state[chat_id] = None
        return True
    return False

# ====== Eid Rules ======
@bot.message_handler(func=lambda m: m.text == 'Eid Rules')
def eid_rules(message):
    text = """🕌 **ঈদের নিয়ম-কানুন**
1. ঈদের নামাজ: 2 রাকাত, 6 তাকবির
2. ফজরের পর গোসল, সুন্দর পোশাক
3. ফিতরা: নামাজের আগে দিতে হবে"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ====== Fun Zone ======
@bot.message_handler(func=lambda m: m.text == 'Fun Zone')
def fun_zone(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('😂 জোকস', '🎲 রিডল', '🔙 ব্যাক')
    bot.send_message(message.chat.id, "🎭 Fun Zone:", reply_markup=markup)
    user_state[message.chat.id] = 'fun_menu'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'fun_menu')
def fun_handler(message):
    if message.text == '😂 জোকস':
        bot.send_message(message.chat.id, "শিক্ষক: 2+2=? ছাত্র: 22 স্যার! 😂")
    elif message.text == '🎲 রিডল':
        bot.send_message(message.chat.id, "4 পা আছে কিন্তু হাঁটতে পারি না। আমি কে?\nউত্তর: টেবিল")
    elif message.text == '🔙 ব্যাক':
        user_state[message.chat.id] = None
        start(message)

# ====== Eid Greeting ======
@bot.message_handler(func=lambda m: m.text == 'Eid Greeting')
def eid_greeting(message):
    bot.send_message(message.chat.id, "কার জন্য শুভেচ্ছা বানাবো? নাম লিখো:")
    user_state[message.chat.id] = 'greeting_name'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'greeting_name')
def greeting_name(message):
    bot.send_message(message.chat.id, f"🌙 {message.text}, ঈদ মোবারক! 🎉")
    user_state[message.chat.id] = None

def run_bot():
    bot.remove_webhook()
    print("Bot polling started")
    bot.polling(none_stop=True, drop_pending_updates=True)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
