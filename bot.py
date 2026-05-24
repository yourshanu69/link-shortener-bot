print("Script started")
import random
import telebot
import random
user_state = {}
from telebot import types
import os
from telebot import types
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import json
import textwrap
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Shanu's Magic Bot is Alive! 🔥"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_files = {}

# ====== OLD 28 TOOLS START ======
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    btn1 = types.KeyboardButton('📷 Image→PDF')
    btn2 = types.KeyboardButton('🔤 Stylish Font')
    btn3 = types.KeyboardButton('🖼️ Sticker')
    btn4 = types.KeyboardButton('📦 Zip')
    btn5 = types.KeyboardButton('💬 Fake Chat')
    btn6 = types.KeyboardButton('🔥 Roast')
    btn7 = types.KeyboardButton('💎 Beauty Meter')
    btn8 = types.KeyboardButton('💰 Celebrity দাম')
    btn9 = types.KeyboardButton('🎲 ভাগ্য গণনা')
    btn10 = types.KeyboardButton('🔗 Deep Link')
    btn11 = types.KeyboardButton('💸 Fake রিচার্জ')
    btn12 = types.KeyboardButton('🐕 কুত্তা Roast')
    btn13 = types.KeyboardButton('🎭 Prank Voice')
    btn14 = types.KeyboardButton('❤️ Love ক্যালকুলেটর')
    btn15 = types.KeyboardButton('🗣️ TTS')
    btn16 = types.KeyboardButton('🗑️ Remove BG')
    btn17 = types.KeyboardButton('🔄 Image→Link')
    btn18 = types.KeyboardButton('📄 PDF→Text')
    btn19 = types.KeyboardButton('📝 Text→PDF')
    btn20 = types.KeyboardButton('🔒 Password PDF')
    btn21 = types.KeyboardButton('🎙️ Voice Change')
    btn22 = types.KeyboardButton('💼 Job CV')
    btn23 = types.KeyboardButton('🏆 Topper Result')
    btn24 = types.KeyboardButton('💰 Fake Payment')
    btn25 = types.KeyboardButton('🎬 YouTube Thumbnail')
    btn26 = types.KeyboardButton('📰 Fake News')
    btn27 = types.KeyboardButton('🏦 Bank Balance SS')
    btn28 = types.KeyboardButton('🎮 FF Diamond')

    # NEW 4 TOOLS
    btn29 = types.KeyboardButton('🎨 Banner Creator')
    btn30 = types.KeyboardButton('🕌 Eid Rules')
    btn31 = types.KeyboardButton('🎭 Fun Zone')
    btn32 = types.KeyboardButton('💌 Eid Greeting')

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10,
               btn11, btn12, btn13, btn14, btn15, btn16, btn17, btn18, btn19, btn20,
               btn21, btn22, btn23, btn24, btn25, btn26, btn27, btn28,
               btn29, btn30, btn31, btn32)

    bot.send_message(chat_id, "🔥 **বস আসছে! 32টা টুল নিয়ে হাজির** 😎\n\nমজা + কাজ সব হবে এক জায়গায় 👇", reply_markup=markup)
    user_state[chat_id] = None
    user_files[chat_id] = []

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_all(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    text = message.text if message.text else ""

    # Banner state handler
    if handle_banner_state(message, state, chat_id, text):
        return

    # Old 28 tools
    if text == '📷 Image→PDF':
        user_state[chat_id] = "image_pdf"
        user_files[chat_id] = []
        bot.send_message(chat_id, "📷 **Image গুলা পাঠাও**\n\nএকসাথে অনেকগুলা Image দিতে পারো। শেষ হলে 'Done' লিখো।")
        return
    elif text == '🔤 Stylish Font':
        user_state[chat_id] = "font"
        bot.send_message(chat_id, "🔤 **Text লিখো**\n\nতোমার Text টারে Stylish বানায় দিবো।")
        return
    elif text == '🖼️ Sticker':
        user_state[chat_id] = "sticker"
        bot.send_message(chat_id, "🖼️ **Photo পাঠাও**\n\nSticker বানায় দিবো Telegram এর জন্য।")
        return
    elif text == '📦 Zip':
        user_state[chat_id] = "zip"
        user_files[chat_id] = []
        bot.send_message(chat_id, "📦 **File গুলা পাঠাও**\n\nসব File একটা Zip এ ভরে দিবো। শেষ হলে 'Done' লিখো।")
        return
    elif text == '💬 Fake Chat':
        user_state[chat_id] = "fake_chat_name1"
        bot.send_message(chat_id, "💬 **Fake Chat বানাবা?**\n\nপ্রথম জনের নাম লিখো:")
        return
    elif text == '🔥 Roast':
        user_state[chat_id] = "roast"
        bot.send_message(chat_id, "🔥 **কারে Roast করবা?**\n\nনাম লিখো বা Photo পাঠাও। আমি Roast করে দিবো 😈")
        return
    elif text == '💎 Beauty Meter':
        user_state[chat_id] = "beauty"
        bot.send_message(chat_id, "💎 **Photo পাঠাও**\n\nAI দিয়ে Beauty Score বের করে দিবো 100 তে কত 😍")
        return
    elif text == '💰 Celebrity দাম':
        user_state[chat_id] = "celebrity"
        bot.send_message(chat_id, "💰 **Celebrity এর নাম লিখো**\n\nআমি বলে দিবো তার বর্তমান বাজার দাম কত 😂")
        return
    elif text == '🎲 ভাগ্য গণনা':
        user_state[chat_id] = "luck"
        bot.send_message(chat_id, "🎲 **নাম লিখো**\n\nতোমার আজকের ভাগ্য গণনা করে দিবো 🔮")
        return
    elif text == '🔗 Deep Link':
        user_state[chat_id] = "deeplink"
        bot.send_message(chat_id, "🔗 **Link পাঠাও**\n\nShort + Tracking সহ Deep Link বানায় দিবো।")
        return
    elif text == '💸 Fake রিচার্জ':
        user_state[chat_id] = "recharge"
        bot.send_message(chat_id, "💸 **Operator + Amount লিখো**\n\nযেমন: Grameenphone 500\nFake রিচার্জ SS বানায় দিবো 😂")
        return
    elif text == '🐕 কুত্তা Roast':
        user_state[chat_id] = "dog_roast"
        bot.send_message(chat_id, "🐕 **কুত্তার Photo পাঠাও**\n\nRoast করে Caption সহ দিবো 😈")
        return
    elif text == '🎭 Prank Voice':
        user_state[chat_id] = "prank_voice"
        bot.send_message(chat_id, "🎭 **Text লিখো**\n\nPrank Voice বানায় দিবো। ভয়েস শুনে বন্ধুরা ভয় পাবে 😂")
        return
    elif text == '❤️ Love ক্যালকুলেটর':
        user_state[chat_id] = "love_calc_name1"
        bot.send_message(chat_id, "❤️ **Love Calculator**\n\nপ্রথম জনের নাম লিখো:")
        return
    elif text == '🗣️ TTS':
        user_state[chat_id] = "tts"
        bot.send_message(chat_id, "🗣️ **Text লিখো**\n\nVoice বানায় দিবো বাংলা/English।")
        return
    elif text == '🗑️ Remove BG':
        user_state[chat_id] = "remove_bg"
        bot.send_message(chat_id, "🗑️ **Photo পাঠাও**\n\nBackground Remove করে দিবো 1 Second এ।")
        return
    elif text == '🔄 Image→Link':
        user_state[chat_id] = "image_link"
        bot.send_message(chat_id, "🔄 **Photo পাঠাও**\n\nDirect Link বানায় দিবো।")
        return
    # বাকি 11টা টুলের হ্যান্ডলার তোমার আগের মতোই থাকবে
# ====== OLD 28 TOOLS END ======

# ====== NEW TOOL 1: BANNER CREATOR ======
TEMPLATES = {
    "eid_1": "templates/eid_1.png", "eid_2": "templates/eid_2.png",
    "eid_3": "templates/eid_3.png", "eid_4": "templates/eid_4.png",
    "eid_5": "templates/eid_5.png", "eid_6": "templates/eid_6.png",
    "eid_7": "templates/eid_7.png", "eid_8": "templates/eid_8.png",
    "eid_9": "templates/eid_9.png", "eid_10": "templates/eid_10.png",
    "eid_11": "templates/eid_11.png", "eid_12": "templates/eid_12.png"
}
PREMIUM_USERS = [123456789] # @userinfobot থেকে তোমার ID বসাও

@bot.message_handler(func=lambda m: m.text == '🎨 Banner Creator')
def banner_start(message):
    chat_id = message.chat.id
    is_premium = message.from_user.id in PREMIUM_USERS
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(f"T{i}", callback_data=f"tpl_eid_{i}") for i in range(1, 13)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ বাতিল", callback_data="tpl_cancel"))
    bot.send_message(chat_id, f"{'✨ Premium' if is_premium else '🆓 Free'}\n12টা টেমপ্লেট থেকে বেছে নাও:", reply_markup=markup)
    user_state[chat_id] = 'banner_tpl'
    user_state[f'{chat_id}_prem'] = is_premium

@bot.callback_query_handler(func=lambda call: call.data.startswith('tpl_'))
def banner_tpl_select(call):
    chat_id = call.message.chat.id
    if call.data == 'tpl_cancel':
        bot.edit_message_text("বাতিল", chat_id, call.message_id)
        user_state[chat_id] = None
        return
    user_state[chat_id] = 'banner_photo'
    user_state[f'{chat_id}_tpl'] = call.data.replace('tpl_', '')
    bot.edit_message_text("✅ টেমপ্লেট সিলেক্ট হলো\n1️⃣ ছবি পাঠাও", chat_id, call.message_id)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'banner_photo', content_types=['photo'])
def banner_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id
    photo_path = f"output/{chat_id}.jpg"
    os.makedirs("output", exist_ok=True)
    with open(photo_path, 'wb') as f:
        f.write(bot.download_file(bot.get_file(file_id).file_path))
    user_state[chat_id] = 'banner_name'
    user_state[f'{chat_id}_photo'] = photo_path
    bot.send_message(chat_id, "2️⃣ নাম লিখো:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'banner_name')
def banner_name(message):
    user_state[message.chat.id] = 'banner_addr'
    user_state[f'{message.chat.id}_name'] = message.text
    bot.send_message(message.chat.id, "3️⃣ ঠিকানা/পদবি লিখো:")

def handle_banner_state(message, state, chat_id, text):
    if state == 'banner_addr':
        data = {
            'tpl': user_state[f'{chat_id}_tpl'],
            'photo': user_state[f'{chat_id}_photo'],
            'name': user_state[f'{chat_id}_name'],
            'addr': text,
            'prem': user_state[f'{chat_id}_prem']
        }
        bot.send_message(chat_id, "⏳ ব্যানার বানাচ্ছি...")
        path = create_banner(data)
        if path:
            bot.send_photo(chat_id, open(path, 'rb'), caption="✅ রেডি! 🔥")
        else:
            bot.send_message(chat_id, "❌ Error")
        user_state[chat_id] = None
        return True
    return False

def create_banner(d):
    try:
        tpl_path = TEMPLATES[d['tpl']]
        img = Image.open(tpl_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        user_img = Image.open(d['photo']).resize((420, 420))
        img.paste(user_img, (330, 200))
        font1 = ImageFont.truetype("fonts/SolaimanLipi.ttf", 90)
        font2 = ImageFont.truetype("fonts/SolaimanLipi.ttf", 60)
        draw.text((540, 680), d['name'], font=font1, fill="white", anchor="mm")
        draw.text((540, 780), d['addr'], font=font2, fill="#FFD700", anchor="mm")
        if not d['prem']:
            draw.text((540, 1050), "Made with Shanu's Bot", font=font2, fill="gray", anchor="mm")
        os.makedirs("output", exist_ok=True)
        out = f"output/banner_{d['tpl']}.png"
        img.save(out, quality=95)
        return out
    except Exception as e:
        print(e)
        return None

# ====== NEW TOOL 2: EID RULES ======
@bot.message_handler(func=lambda m: m.text == '🕌 Eid Rules')
def eid_rules(message):
    text = """🕌 **ঈদুল ফিতরের নিয়ম-কানুন**

**১. ঈদের নামাজ:**
- সময়: সূর্য উঠার 20 মিনিট পর থেকে জোহরের আগ পর্যন্ত
- 2 রাকাত, অতিরিক্ত 6 তাকবির

**২. সুন্নত আমল:**
- ফজরের পর গোসল করা
- সুন্দর পোশাক পরা, আতর লাগানো
- মিষ্টি খেয়ে ঈদগাহে যাওয়া

**৩. ফিতরা:**
- ঈদের নামাজের আগে দিতে হবে
- জনপ্রতি 100-150 টাকা আনুমানিক"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ====== NEW TOOL 3: FUN ZONE ======
fun_jokes = [
    "শিক্ষক: 2+2=? ছাত্র: 22 স্যার! শিক্ষক: কিভাবে? ছাত্র: 2 পাশে 2 বসাই দিছি 😂",
    "বউ: আমি মোটা? স্বামী: না তুমি গোলগাল সুন্দর 😍",
    "প্রেমিক: তুমি আমার জীবন। প্রেমিকা: তাহলে BP লো কেন? 😂"
]

@bot.message_handler(func=lambda m: m.text == '🎭 Fun Zone')
def fun_zone(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('😂 জোকস', '🎲 রিডল', '🔥 ট্রুথ-ডেয়ার', '🔙 ব্যাক')
    bot.send_message(message.chat.id, "🎭 Fun Zone এ স্বাগতম! কি চাও?", reply_markup=markup)
    user_state[message.chat.id] = 'fun_menu'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'fun_menu')
def fun_handler(message):
    chat_id = message.chat.id
    text = message.text
    if text == '😂 জোকস':
        bot.send_message(chat_id, random.choice(fun_jokes))
    elif text == '🎲 রিডল':
        bot.send_message(chat_id, "আমার 4টা পা আছে কিন্তু হাঁটতে পারি না। আমি কে?\nউত্তর: টেবিল 🪑")
    elif text == '🔥 ট্রুথ-ডেয়ার':
        bot.send_message(chat_id, "ট্রুথ: জীবনের সবচেয়ে লজ্জার মুহূর্ত কি?\nডেয়ার: 10 সেকেন্ড নাচো 💃")
    elif text == '🔙 ব্যাক':
        user_state[chat_id] = None
        start(message)

# ====== NEW TOOL 4: EID GREETING ======
@bot.message_handler(func=lambda m: m.text == '💌 Eid Greeting')
def eid_greeting(message):
    bot.send_message(message.chat.id, "💌 কার জন্য শুভেচ্ছা বানাবো? নাম লিখো:")
    user_state[message.chat.id] = 'greeting_name'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'greeting_name')
def greeting_name(message):
    name = message.text
    greetings = [
        f"🌙 {name} ভাই/আপু, ঈদ মোবারক! আল্লাহ তোমার জীবন সুখে ভরে দিক।",
        f"💖 প্রিয় {name}, ঈদের খুশি তোমার ঘরে আসুক। ভালো থেকো।",
        f"✨ {name}, ঈদের দিনে দোয়া করি তোমার সব স্বপ্ন পূরণ হোক।"
    ]
    bot.send_message(message.chat.id, random.choice(greetings))
    user_state[message.chat.id] = None

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot started polling")
    bot.polling(none_stop=True)
