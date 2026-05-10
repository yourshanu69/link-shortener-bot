import os
import telebot
import requests
import replicate
import google.generativeai as genai
from telebot import types
from pytube import YouTube
import tempfile
import qrcode
from io import BytesIO

# API Keys Render Environment থেকে নিবে
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REMOVE_BG_KEY = os.getenv("REMOVE_BG_KEY")
REPLICATE_TOKEN = os.getenv("REPLICATE_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
if REPLICATE_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

user_state = {}

# /start মেনু - Contact বাটন বাদ
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🎬 YT Video", callback_data="yt_video")
    btn2 = types.InlineKeyboardButton("🎵 MP3 গান", callback_data="yt_audio")
    btn3 = types.InlineKeyboardButton("🤖 AI Chat", callback_data="ai_chat")
    btn4 = types.InlineKeyboardButton("✍️ ছন্দমালা", callback_data="poem")
    btn5 = types.InlineKeyboardButton("🖼️ Photo Editor", callback_data="photo_edit")
    btn6 = types.InlineKeyboardButton("🎥 Photo→Video", callback_data="photo_video")
    btn7 = types.InlineKeyboardButton("🖼️ QR Code", callback_data="qr")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    bot.send_message(message.chat.id, "🔥 **All-in-One Super Bot** 🔥\n\nকি করতে চাও ভাই?", reply_markup=markup, parse_mode="Markdown")

# বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "yt_video":
        user_state[chat_id] = "yt_video"
        bot.send_message(chat_id, "🎬 YouTube ভিডিওর লিংক দাও:")
    elif call.data == "yt_audio":
        user_state[chat_id] = "yt_audio"
        bot.send_message(chat_id, "🎵 গানের নাম বা YouTube লিংক দাও:")
    elif call.data == "ai_chat":
        user_state[chat_id] = "ai_chat"
        bot.send_message(chat_id, "🤖 আমাকে যেকোনো প্রশ্ন করো:")
    elif call.data == "poem":
        user_state[chat_id] = "poem"
        bot.send_message(chat_id, "✍️ বয়স কত? লিখো: `বয়স 20, প্রেমের কবিতা`")
    elif call.data == "photo_edit":
        user_state[chat_id] = "photo_edit"
        bot.send_message(chat_id, "🖼️ ছবি পাঠাও। Background Remove করে দিবো:")
    elif call.data == "photo_video":
        user_state[chat_id] = "photo_video"
        bot.send_message(chat_id, "🎥 ছবি পাঠাও। আমি ভিডিও বানায় দিবো:")
    elif call.data == "qr":
        user_state[chat_id] = "qr"
        bot.send_message(chat_id, "🖼️ QR এর জন্য লেখা বা লিংক দাও:")

# মেসেজ হ্যান্ডলার
@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)

    try:
        # 1. YT Video Download
        if state == "yt_video" and message.text:
            msg = bot.send_message(chat_id, "⏳ ডাউনলোড হচ্ছে...")
            yt = YouTube(message.text)
            stream = yt.streams.get_highest_resolution()
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                stream.download(filename=tmp.name)
                bot.send_video(chat_id, open(tmp.name, 'rb'), caption=f"✅ {yt.title}")
            os.remove(tmp.name)
            bot.delete_message(chat_id, msg.message_id)

        # 2. MP3 Download
        elif state == "yt_audio" and message.text:
            msg = bot.send_message(chat_id, "⏳ MP3 বানাচ্ছি...")
            yt = YouTube(message.text) if "youtube.com" in message.text else YouTube(f"ytsearch:{message.text}").streams[0]
            stream = yt.streams.filter(only_audio=True).first()
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                stream.download(filename=tmp.name)
                bot.send_audio(chat_id, open(tmp.name, 'rb'), title=yt.title)
            os.remove(tmp.name)
            bot.delete_message(chat_id, msg.message_id)

        # 3. AI Chat
        elif state == "ai_chat" and message.text:
            msg = bot.send_message(chat_id, "🤖 ভাবতেছি...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"তুমি বন্ধুর মতো কথা বলো। ইউজার: {message.text}")
            bot.edit_message_text(response.text, chat_id, msg.message_id)

        # 4. ছন্দমালা
        elif state == "poem" and message.text:
            msg = bot.send_message(chat_id, "✍️ কবিতা লিখতেছি...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"তুমি একজন কবি। {message.text} এই বয়স অনুযায়ী সুন্দর ছন্দমালা/গীতিমালা লিখো। 4-6 লাইন।")
