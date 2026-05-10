import os
import telebot
import subprocess
import random
import zipfile
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telebot import types
from flask import Flask
from threading import Thread
from PyPDF2 import PdfMerger

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
user_files = {}

# Random Reply ডাটাবেজ - এক রিপ্লাই বারবার দিবে না
REPLIES = {
    "start": [
        "🔥 বস আসছে! কি হেল্প লাগবে? 👇",
        "ওই যে! Premium টুল বক্স রেডি। কোনটা চালাবা? 😎",
        "আরে ভাই! 11টা পাওয়ারফুল টুল নিয়ে হাজির। চাপ দাও 👇"
    ],
    "compress_wait": [
        "⏳ সাইজ কমাচ্ছি... চা খেয়ে আসো একটু ☕",
        "⏳ ভিডিওটা জিমে পাঠাইছি। চিকন হয়ে আসতেছে 💪",
        "⏳ Compress চলতেছে... MB কমলে খুশিতে নাচবা 💃"
    ],
    "compress_done": [
        "✅ Done বস! ফাইল হালকা হয়ে গেছে। WhatsApp এ পাঠায় দাও 📤",
        "✅ কাজ শেষ! এখন আর 'File too large' আসবে না 😏",
        "✅ নাও ভাই, সাইজ কমায় দিছি। ডাউনলোড করো 📥"
    ],
    "pdf_wait": [
        "⏳ ছবিগুলারে PDF বানায় বিয়ে দিতেছি 💍",
        "⏳ PDF রেডি হচ্ছে... একটু সবুর করো বস 🫡",
        "⏳ সব ছবি এক ফাইলে ঢুকাচ্ছি... 📄"
    ],
    "error": [
        "❌ উফ! একটু গন্ডগোল হইছে। আবার ট্রাই করো তো ভাই 🙏",
        "❌ Error খাইছি! ফাইলটা ঠিক আছে তো? আরেকবার পাঠাও 😅",
        "❌ ধুর! কাজ হইলো না। /start দিয়ে নতুন করে শুরু করো"
    ],
    "roast_intro": [
        "🔥 Roast রেডি! কে খাবে? 😈",
        "🔥 গরম গরম Roast এসে গেছে 👇",
        "🔥 কার ইজ্জতের ফালুদা বানাবো? নাম বলো 🤣"
    ]
}

ROAST_LINES = [
    "{name} কে দেখলে WiFi ও Password ভুলে যায় 😂",
    "{name} এর মাথায় Google Map ঢুকায় দিলেও রাস্তা খুঁজে পাবে না 🤣",
    "{name} এত Slow, শামুক ওর কাছে দৌড় প্রতিযোগিতায় হারে 🐌",
    "{name} কে Mirror দেখলে Mirror ও বলে 'Error 404' 😜",
    "{name} এর ফোনের চার্জ 1% এ আসলে ফোন নিজেই Off হয়ে যায় লজ্জায় 🔋",
    "{name} Free Fire খেলে Free তে মরে যাওয়ার জন্য 🪂"
]

FONTS = {
    "bold": lambda t: ''.join(chr(ord(c) + 0x1D5D4 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D5EE - 0x61) if 'a' <= c <= 'z' else c for c in t),
    "italic": lambda t: ''.join(chr(ord(c) + 0x1D608 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D622 - 0x61) if 'a' <= c <= 'z' else c for c in t)
}

def random_reply(key):
    return random.choice(REPLIES.get(key, ["✅ Done"]))

def cleanup(chat_id):
    if chat_id in user_files:
        for f in user_files[chat_id]:
            if os.path.exists(f): os.remove(f)
        del user_files[chat_id]
    if chat_id in user_state: del user_state[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    cleanup(message.chat.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🗜️ Compress", "📄 Image→PDF", "✂️ Video Cut", "🎵 Video→MP3", "🖼️ Watermark", "🔤 Stylish Font", "🖼️ Sticker", "📦 Zip", "🎭 Prank Voice", "💬 Fake Chat", "🔥 Roast")
    bot.send_message(message.chat.id, random_reply("start"), reply_markup=markup)

@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_files(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    if not state:
        bot.send_message(chat_id, "আগে /start দিয়ে কি করবা সিলেক্ট করো ভাই")
        return

    try:
        file_id = message.photo[-1].file_id if message.photo else message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"/tmp/{chat_id}_{os.path.basename(file_info.file_path)}"
        with open(filename, 'wb') as f: f.write(downloaded)

        if chat_id not in user_files: user_files[chat_id] = []
        user_files[chat_id].append(filename)

        if state == "img2pdf":
            bot.send_message(chat_id, f"✅ {len(user_files[chat_id])}টা নিছি। আরো থাকলে দাও, নাই
