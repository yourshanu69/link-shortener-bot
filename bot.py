print("Script started")
import os
import random
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ====== Flask App ======
app = Flask(__name__)

@app.route('/')
def home():
    return "Shanu's Magic Bot is Alive! 🔥"

# ====== Bot Setup ======
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
user_files = {}

PREMIUM_USERS = [123456789] # @userinfobot থেকে ID বসাও

# ====== /start Menu ======
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    buttons = [
        '📷 Image→PDF', '🔤 Stylish Font', '🖼️ Sticker', '📦 Zip',
        '💬 Fake Chat', '🔥 Roast', '💎 Beauty Meter', '💰 Celebrity দাম',
        '🎲 ভাগ্য গণনা', '🔗 Deep Link', '💸 Fake রিচার্জ', '🐕 কুত্তা Roast',
        '🎭 Prank Voice', '❤️ Love ক্যালকুলেটর', '🗣️ TTS', '🗑️ Remove BG',
        '🔄 Image→Link', '📄 PDF→Text', '📝 Text→PDF', '🔒 Password PDF',
        '🎙️ Voice Change', '💼 Job CV', '🏆 Topper Result', '💰 Fake Payment',
        '🎬 YouTube Thumbnail', '📰 Fake News', '🏦 Bank Balance SS', '🎮 FF Diamond',
        '🎨 Banner Creator', '🕌 Eid Rules', '🎭 Fun Zone', '💌 Eid Greeting'
    ]

    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(chat_id, "🔥 **32টা টুল রেডি** 😎\nনিচ থেকে যেকোনো একটা সিলেক্ট করো 👇",
                     reply_markup=markup, parse_mode="Markdown")
    user_state[chat_id] = None
    user_files[chat_id] = []

# ====== Tool Handlers ======
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document'])
def handle_all(message):
    chat_id = message.chat.id
    text = message.text if message.text else ""

    # Banner state handler first
    if handle_banner_state(message, user_state.get(chat_id), chat_id, text):
        return

    # 32 Tools
    tools = {
        '📷 Image→PDF': "📷 Image→PDF টুল চালু হলো। Image পাঠাও, শেষে 'Done' লিখো।",
        '🔤 Stylish Font': "🔤 Stylish Font: Text লিখো।",
        '🖼️ Sticker': "🖼️ Sticker: Photo পাঠাও।",
        '📦 Zip': "📦 Zip: File পাঠাও, শেষে 'Done' লিখো।",
        '💬 Fake Chat': "💬 Fake Chat: প্রথম জনের নাম লিখো।",
        '🔥 Roast': "🔥 Roast: কারে roast করবা?",
        '💎 Beauty Meter': "💎 Beauty Meter: Photo পাঠাও।",
        '💰 Celebrity দাম': "💰 Celebrity দাম: নাম লিখো।",
        '🎲 ভাগ্য গণনা': "🎲 ভাগ্য গণনা: নাম লিখো।",
        '🔗 Deep Link': "🔗 Deep Link: Link পাঠাও।",
        '💸 Fake রিচার্জ': "💸 Fake রিচার্জ: Operator + Amount লিখো।",
        '🐕 কুত্তা Roast': "🐕 কুত্তা Roast: Photo পাঠাও।",
        '🎭 Prank Voice': "🎭 Prank Voice: Text লিখো।",
        '❤️ Love ক্যালকুলেটর': "❤️ Love Calculator: প্রথম জনের নাম লিখো।",
        '🗣️ TTS': "🗣️ TTS: Text লিখো।",
        '🗑️ Remove BG': "🗑️ Remove BG: Photo পাঠাও।",
        '🔄 Image→Link': "🔄 Image→Link: Photo পাঠাও।",
        '📄 PDF→Text': "📄 PDF→Text: PDF পাঠাও।",
        '📝 Text→PDF': "📝 Text→PDF: Text লিখো।",
        '🔒 Password PDF': "🔒 Password PDF: PDF + Password দাও।",
        '🎙️ Voice Change': "🎙️ Voice Change: Voice পাঠাও।",
        '💼 Job CV': "💼 Job CV: তথ্য দাও।",
        '🏆 Topper Result': "🏆 Topper Result: নাম + রোল দাও।",
        '💰 Fake Payment': "💰 Fake Payment: Amount লিখো।",
        '🎬 YouTube Thumbnail': "🎬 YouTube Thumbnail: Title লিখো।",
        '📰 Fake News': "📰 Fake News: Headline লিখো।",
        '🏦 Bank Balance SS': "🏦 Bank Balance SS: Amount লিখো।",
        '🎮 FF Diamond': "🎮 FF Diamond: UID দাও।",
        '🎨 Banner Creator': "🎨 Banner Creator শুরু হচ্ছে...",
        '🕌 Eid Rules': "🕌 Eid Rules দেখাচ্ছি...",
        '🎭 Fun Zone': "🎭 Fun Zone খুলছে...",
        '💌 Eid Greeting': "💌 Eid Greeting বানাচ্ছি..."
    }

    if text in tools:
        user_state[chat_id] = text
        bot.send_message(chat_id, tools[text])

        # Special handlers for working tools
        if text == '🎨 Banner Creator':
            banner_start(message)
        elif text == '🕌 Eid Rules':
            eid_rules(message)
        elif text == '🎭 Fun Zone':
            fun_zone(message)
        elif text == '💌 Eid Greeting':
            eid_greeting(message)
    else:
        bot.send_message(chat_id, "মেনু থেকে একটা অপশন সিলেক্ট করো 👇")

# ====== 4 New Tools Implementation ======
TEMPLATES = {f"eid_{i}": f"templates/eid_{i}.png" for i in range(1, 13)}

@bot.message_handler(func=lambda m: m.text == '🎨 Banner Creator')
def banner_start(message):
    chat_id = message.chat.id
    is_premium = message.from_user.id in PREMIUM_USERS
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(f"T{i}", callback_data=f"tpl_eid_{i}") for i in range(1, 13)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ বাতিল", callback_data="tpl_cancel"))
    bot.send_message(chat_id, f"{'✨ Premium' if is_premium else '🆓 Free'}\n12টা টেমপ্লেট:", reply_markup=markup)
    user_state[chat_id] = 'banner_tpl'
    user_state[f'{chat_id}_prem'] = is_premium

@bot.callback_query_handler(func=lambda call: call.data.startswith('tpl_'))
def banner_tpl_select(call):
    chat_id = call.message.chat.id
    if call.data == 'tpl_cancel':
        bot.edit_message_text("বাতিল", chat_id, call.message.id)
        user_state[chat_id] = None
        return
    user_state[chat_id] = 'banner_photo'
    user_state[f'{chat_id}_tpl'] = call.data.replace('tpl_', '')
    bot.edit_message_text("✅ টেমপ্লেট সিলেক্ট হলো\n1️⃣ ছবি পাঠাও", chat_id, call.message.id)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'banner_photo', content_types=['photo'])
def banner_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id
    os.makedirs("output", exist_ok=True)
    photo_path = f"output/{chat_id}.jpg"
    with open(photo_path, 'wb') as f:
        f.write(bot.download_file(bot.get_file(file_id).file_path))
    user_state[chat_id] = 'banner_name'
    user_state[f'{chat_id}_photo'] = photo_path
    bot.send_message(chat_id, "2️⃣ নাম লিখো:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'banner_name')
def banner_name(message):
    user_state[message.chat.id] = 'banner_addr'
    user_state[f'{message.chat.id}_name'] = message.text
    bot.send_message(message.chat.id, "3️⃣ ঠিকানা লিখো:")

def handle_banner_state(message, state, chat_id, text):
    if state == 'banner_addr':
        bot.send_message(chat_id, "✅ ব্যানার রেডি! Premium না হলে ওয়াটারমার্ক থাকবে।")
        user_state[chat_id] = None
        return True
    return False

@bot.message_handler(func=lambda m: m.text == '🕌 Eid Rules')
def eid_rules(message):
    text = """🕌 **ঈদের নিয়ম-কানুন**

1. ঈদের নামাজ: 2 রাকাত, 6 তাকবির
2. ফজরের পর গোসল, সুন্দর পোশাক
3. ফিতরা: নামাজের আগে দিতে হবে"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '🎭 Fun Zone')
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

@bot.message_handler(func=lambda m: m.text == '💌 Eid Greeting')
def eid_greeting(message):
    bot.send_message(message.chat.id, "কার জন্য শুভেচ্ছা বানাবো? নাম লিখো:")
    user_state[message.chat.id] = 'greeting_name'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'greeting_name')
def greeting_name(message):
    bot.send_message(message.chat.id, f"🌙 {message.text}, ঈদ মোবারক! 🎉")
    user_state[message.chat.id] = None

# ====== Run ======
def run_bot():
    bot.remove_webhook()
    print("Bot polling started")
    try:
        bot.polling(none_stop=True, drop_pending_updates=True)
    except TypeError:
        bot.polling(none_stop=True)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    print(f"Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)
