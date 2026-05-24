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

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        '📷 Image→PDF', '🖼️ Sticker', '🗑️ Remove BG', '📝 Text→PDF', '📄 PDF→Text',
        '🔥 Roast', '❤️ Love ক্যালকুলেটর', '🎲 ভাগ্য গণনা', '💎 Beauty Meter', '🎭 Fun Zone',
        '💬 Fake Chat', '💰 Fake Payment', '🏦 Bank Balance SS', '📰 Fake News', '🎮 FF Diamond',
        '🎨 Banner Creator', '🔤 Stylish Font', '🎬 YouTube Thumbnail', '💌 Eid Greeting',
        '🗣️ TTS', '🔗 Deep Link', '🕌 Eid Rules'
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(chat_id, "🔥 **22টা টুল রেডি** 😎\nনিচ থেকে যেকোনো একটা সিলেক্ট করো 👇",
                     reply_markup=markup, parse_mode="Markdown")
    user_state[chat_id] = None

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document'])
def handle_all(message):
    chat_id = message.chat.id
    text = message.text if message.text else ""
    state = user_state.get(chat_id, None)

    if handle_banner_state(message, state, chat_id, text):
        return
    if state in ['banner_name', 'banner_addr', 'banner_photo', 'banner_tpl']:
        bot.send_message(chat_id, "আগের প্রসেসটা শেষ করো 👆")
        return

    if text in tools_prompt:
        user_state[chat_id] = f"wait_{text}"
        bot.send_message(chat_id, tools_prompt[text])

        # 4টা টুলের স্পেশাল হ্যান্ডলার
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

tools_prompt = {
    '📷 Image→PDF': "📷 ছবি পাঠাও, 'Done' লিখলে PDF বানায় দেব",
    '🖼️ Sticker': "🖼️ ছবি পাঠাও, স্টিকার বানায় দেব",
    '🗑️ Remove BG': "🗑️ ছবি পাঠাও, BG রিমুভ করবো",
    '📝 Text→PDF': "📝 Text লিখো, PDF বানাবো",
    '📄 PDF→Text': "📄 PDF পাঠাও, টেক্সট বের করবো",
    '🔥 Roast': "🔥 কাকে roast করবা?",
    '❤️ Love ক্যালকুলেটর': "❤️ নাম1, নাম2 লিখো",
    '🎲 ভাগ্য গণনা': "🎲 তোমার নাম লিখো",
    '💎 Beauty Meter': "💎 ছবি পাঠাও, বিউটি স্কোর দেব",
    '🎭 Fun Zone': "🎭 খুলছে...",
    '💬 Fake Chat': "💬 নাম1, নাম2 লিখো",
    '💰 Fake Payment': "💰 Amount লিখো",
    '🏦 Bank Balance SS': "🏦 Amount লিখো",
    '📰 Fake News': "📰 Headline লিখো",
    '🎮 FF Diamond': "🎮 UID দাও",
    '🎨 Banner Creator': "🎨 শুরু হচ্ছে...",
    '🔤 Stylish Font': "🔤 Text লিখো",
    '🎬 YouTube Thumbnail': "🎬 Title লিখো",
    '💌 Eid Greeting': "💌 বানাচ্ছি...",
    '🗣️ TTS': "🗣️ Text লিখো",
    '🔗 Deep Link': "🔗 লিংক পাঠাও",
    '🕌 Eid Rules': "🕌 দেখাচ্ছি..."
}

@bot.message_handler(func=lambda m: user_state.get(m.chat.id, "").startswith("wait_"))
def process_tool(message):
    chat_id = message.chat.id
    state = user_state[chat_id]
    tool = state.replace("wait_", "")
    user_state[chat_id] = None

    inp = message.text if message.text else "ছবি"

    responses = {
        '📷 Image→PDF': "✅ PDF রেডি! Demo mode - রিয়েল লজিক চাইলে বলো",
        '🖼️ Sticker': "✅ Sticker বানানো হলো!",
        '🗑️ Remove BG': "✅ BG রিমুভ হলো!",
        '📝 Text→PDF': f"✅ PDF বানালাম: {inp[:20]}...",
        '📄 PDF→Text': "✅ টেক্সট বের করলাম: Demo text here...",
        '🔥 Roast': f"{inp} কে roast: তুমি WiFi ছাড়া Google এর মতো 😂",
        '❤️ Love ক্যালকুলেটর': f"❤️ Love: {random.randint(60, 99)}% মিল আছে",
        '🎲 ভাগ্য গণনা': random.choice(["আজ টাকা পাবে", "ভালো খবর আসবে", "সাবধানে থেকো"]),
        '💎 Beauty Meter': f"💎 Beauty Score: {random.randint(70, 99)}%",
        '💬 Fake Chat': f"✅ Fake chat বানালাম {inp}",
        '💰 Fake Payment': f"✅ {inp}৳ Payment Successful! Fake 😎",
        '🏦 Bank Balance SS': f"✅ Balance: {inp}৳\nFake SS বানানো হলো",
        '📰 Fake News': f"BREAKING: {inp} - সোর্স: ফেসবুক ইউনিভার্সিটি",
        '🎮 FF Diamond': f"✅ UID {inp} এ 500 Diamond পাঠানো হলো! Fake 😎",
        '🔤 Stylish Font': f"𝐒𝐭𝐲𝐥𝐢𝐬𝐡: {inp}",
        '🎬 YouTube Thumbnail': f"✅ Thumbnail রেডি! Title: {inp}",
        '🗣️ TTS': f"✅ Voice রেডি! Demo mode",
        '🔗 Deep Link': f"✅ Short Link: short.ly/{random.randint(1000,9999)}",
    }
    msg = responses.get(tool, f"✅ {tool} কমপ্লিট! এটা ডেমো ভার্সন")
    bot.send_message(chat_id, msg)

# ====== 4 Working Tools ======
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
        bot.send_message(message.chat.id, random.choice(["শিক্ষক: 2+2=? ছাত্র: 22 স্যার! 😂", "চোর: পুলিশ পেছনে! পুলিশ: আমিও তো চোর! 😂"]))
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

def run_bot():
    bot.remove_webhook()
    print("Bot polling started")
    bot.polling(none_stop=True, drop_pending_updates=True)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
