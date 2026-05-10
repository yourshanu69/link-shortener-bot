import os
import telebot
import requests
import replicate
import google.generativeai as genai
from telebot import types
from pytube import YouTube, Search
import tempfile
import qrcode
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REMOVE_BG_KEY = os.getenv("REMOVE_BG_KEY")
REPLICATE_TOKEN = os.getenv("REPLICATE_TOKEN")
WEATHER_API = os.getenv("WEATHER_API")

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
if REPLICATE_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

user_state = {}

# /start + কিবোর্ড
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🎬 YT Video")
    btn2 = types.KeyboardButton("🎵 MP3 গান")
    btn3 = types.KeyboardButton("🤖 AI Chat")
    btn4 = types.KeyboardButton("✍️ ছন্দমালা")
    btn5 = types.KeyboardButton("🖼️ Photo Editor")
    btn6 = types.KeyboardButton("🎥 Photo→Video")
    btn7 = types.KeyboardButton("🖼️ QR Code")
    btn8 = types.KeyboardButton("📱 Insta Reel")
    btn9 = types.KeyboardButton("🌤️ Weather")
    btn10 = types.KeyboardButton("🌐 Translate")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    bot.send_message(message.chat.id, "🔥 **All-in-One Super Bot 10-in-1** 🔥\n\nনিচের কিবোর্ড থেকে সিলেক্ট করো বা / চেপে Menu দেখো 👇", reply_markup=markup)

# কমান্ড হ্যান্ডলার - / চাপলে যেন কাজ করে
@bot.message_handler(commands=['ytvideo', 'ytaudio', 'aichat', 'poem', 'photoedit', 'photovideo', 'qrcode', 'insta', 'weather', 'translate'])
def command_handler(message):
    chat_id = message.chat.id
    cmd = message.text[1:]  # / বাদ দিয়ে
    
    if cmd == "ytvideo":
        user_state[chat_id] = "yt_video"
        bot.send_message(chat_id, "🎬 YouTube ভিডিওর লিংক দাও:")
    elif cmd == "ytaudio":
        user_state[chat_id] = "yt_audio"
        bot.send_message(chat_id, "🎵 গানের নাম বা YouTube লিংক দাও:")
    elif cmd == "aichat":
        user_state[chat_id] = "ai_chat"
        bot.send_message(chat_id, "🤖 আমাকে যেকোনো প্রশ্ন করো:")
    elif cmd == "poem":
        user_state[chat_id] = "poem"
        bot.send_message(chat_id, "✍️ বয়স কত? লিখো: `বয়স 20, প্রেমের কবিতা`")
    elif cmd == "photoedit":
        user_state[chat_id] = "photo_edit"
        bot.send_message(chat_id, "🖼️ ছবি পাঠাও। Background Remove করে দিবো:")
    elif cmd == "photovideo":
        user_state[chat_id] = "photo_video"
        bot.send_message(chat_id, "🎥 ছবি পাঠাও। আমি ভিডিও বানায় দিবো:")
    elif cmd == "qrcode":
        user_state[chat_id] = "qr"
        bot.send_message(chat_id, "🖼️ QR এর জন্য লেখা বা লিংক দাও:")
    elif cmd == "insta":
        user_state[chat_id] = "insta"
        bot.send_message(chat_id, "📱 Instagram Reel/Post এর লিংক দাও:")
    elif cmd == "weather":
        user_state[chat_id] = "weather"
        bot.send_message(chat_id, "🌤️ শহরের নাম লিখো: `Dhaka`")
    elif cmd == "translate":
        user_state[chat_id] = "translate"
        bot.send_message(chat_id, "🌐 যেকোনো ভাষায় লিখো। আমি বাংলা/ইংলিশে ট্রান্সলেট করে দিবো:")

# কিবোর্ড বাটন + টেক্সট হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_keyboard(message):
    chat_id = message.chat.id
    text = message.text
    state = user_state.get(chat_id)

    # কিবোর্ডের বাটন চেক
    if text == "🎬 YT Video":
        user_state[chat_id]
