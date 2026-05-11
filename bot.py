import os
import telebot
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

user_state = {}
user_files = {}

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
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, 
               btn11, btn12, btn13, btn14, btn15, btn16, btn17, btn18, btn19, btn20,
               btn21, btn22, btn23, btn24, btn25, btn26, btn27, btn28)
    
    bot.send_message(chat_id, "🔥 **বস আসছে! 28টা টুল নিয়ে হাজির** 😎\n\nমজা + কাজ সব হবে এক জায়গায় 👇", reply_markup=markup)
    user_state[chat_id] = None
    user_files[chat_id] = []

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_all(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    text = message.text if message.text else ""
    
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
        bot.send_message(chat_id, "💸 **Operator + Amount লিখো**\n\nযেমন: Grameenphone 500\n\nFake রিচার্জ SS বানায় দিবো 😂")
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
    elif text == '📄 PDF→Text':
        user_state[chat_id] = "pdf_text"
        bot.send_message(chat_id, "📄 **PDF File পাঠাও**\n\nসব Text Extract করে দিবো।")
        return
    elif text == '📝 Text→PDF':
        user_state[chat_id] = "text_pdf"
        bot.send_message(chat_id, "📝 **Text লিখো**\n\nPDF বানায় দিবো সুন্দর করে।")
        return
    elif text == '🔒 Password PDF':
        user_state[chat_id] = "pdf_pass"
        bot.send_message(chat_id, "🔒 **PDF File পাঠাও**\n\nতারপর Password দিবো। Lock করে দিবো।")
        return
    elif text == '🎙️ Voice Change':
        user_state[chat_id] = "voice_change"
        bot.send_message(chat_id, "🎙️ **Voice পাঠাও**\n\nমেয়ে/বাচ্চা/রোবট Voice এ Convert করে দিবো।")
        return
    elif text == '💼 Job CV':
        user_state[chat_id] = "cv_name"
        bot.send_message(chat_id, "💼 **Job CV Maker**\n\nতোমার নাম লিখো:")
        return
    elif text == '🏆 Topper Result':
        user_state[chat_id] = "topper"
        bot.send_message(chat_id, "🏆 **নাম + GPA লিখো**\n\nযেমন: Sakib 5.00\n\nTopper Result Card বানায় দিবো 😂")
        return
    elif text == '💰 Fake Payment':
        user_state[chat_id] = "fake_payment"
        bot.send_message(chat_id, "💰 **Amount + Number লিখো**\n\nযেমন: 5000 01712345678\n\nbKash/Nagad SS বানায় দিবো।")
        return
    elif text == '🎬 YouTube Thumbnail':
        user_state[chat_id] = "yt_thumb"
        bot.send_message(chat_id, "🎬 **Title লিখো**\n\nViral YouTube Thumbnail বানায় দিবো।")
        return
    elif text == '📰 Fake News':
        user_state[chat_id] = "fake_news"
        bot.send_message(chat_id, "📰 **Headline লিখো**\n\nProthom Alo Style Fake News বানায় দিবো 😂")
        return
    elif text == '🏦 Bank Balance SS':
        user_state[chat_id] = "bank_balance"
        bot.send_message(chat_id, "🏦 **Bank + Amount লিখো**\n\nযেমন: DBBL 500000\n\nBank Balance SS বানায় দিবো।")
        return
    elif text == '🎮 FF Diamond':
        user_state[chat_id] = "ff_diamond"
        bot.send_message(chat_id, "🎮 **UID + Diamond লিখো**\n\nযেমন: 12345678 10000\n\nFree Fire Diamond Top-up SS বানায় দিবো।")
        return
    
    try:
        if state == "font":
            fonts = {"bold": "**{}**", "italic": "__{}__", "mono": "`{}`", "strike": "~~{}~~"}
            styled = "\n\n".join([f"{name.title()}:\n{style.format(text)}" for name, style in fonts.items()])
            bot.send_message(chat_id, f"✅ **Stylish Font Ready:**\n\n{styled}")
            user_state[chat_id] = None; start(message)
            return
        elif state == "roast":
            roast_list = ["তোরে দেখলে Google ও বলে 'No Results Found' 😂", "তুই এত কালা যে রাতের বেলায় তোরে খুঁজতে Torch লাগে 💀", "তোর Brain এর Storage Full, নতুন কিছু Install হয় না 🤣"]
            import random
            bot.send_message(chat_id, f"🔥 **Roast:**\n\n{random.choice(roast_list)}")
            user_state[chat_id] = None; start(message)
            return
        else:
            bot.send_message(chat_id, "❌ **বুঝি নাই ভাই**\n\n/start দিয়ে আবার Try করো।")
            user_state[chat_id] = None
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}")
        user_state[chat_id] = None

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
