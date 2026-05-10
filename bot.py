import os
import telebot
import random
import zipfile
import textwrap
import hashlib
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

REPLIES = {
    "start": ["🔥 বস আসছে! 12টা টুল রেডি 😎", "ওই যে! Premium বট রেডি 👇"],
    "error": ["❌ উফ! আবার ট্রাই করো 🙏", "❌ কাজ হইলো না ভাই। /start দাও"]
}

ROAST_LINES = [
    "{name} কে দেখলে WiFi ও Password ভুলে যায় 😂",
    "{name} এর মাথায় Google Map ঢুকায় দিলেও রাস্তা খুঁজে পাবে না 🤣",
    "{name} এত Slow, শামুক ওর কাছে হারে 🐌",
    "{name} কে Mirror দেখলে Mirror বলে 'Error 404' 😜"
]

KUTTA_ROAST = [
    "🐕 {name} হইলো এলাকার সার্টিফাইড কুত্তা। ঘেউ ঘেউ ছাড়া কিছু পারে না 😂",
    "🦴 {name} কে হাড্ডি দিলে নিজের বাপকেও ভুলে যায় 🤣",
    "🐕 {name} এর লেজ সোজা হবে না। জন্মগত কুত্তা 😜"
]

BEAUTY_COMMENTS = [
    "মাশাল্লাহ! নায়ক/নায়িকা ফেইল 💖 স্কোর: {score}/100",
    "ভাই তুমি তো Filter এর বাপ! 🔥 স্কোর: {score}/100",
    "10 এ 10! Camera ও লজ্জা পাইছে 📸 স্কোর: {score}/100"
]

CELEB_PRICE = ["💰 {name} এর বাজার দর: **{price} কোটি টাকা**! 📞"]
FORTUNE = ["🔮 {name}, আগামী মাসে তোমার বিকাশে **{amount} টাকা** আসবে! 💪"]

FONTS = {
    "bold": lambda t: ''.join(chr(ord(c) + 0x1D5D4 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D5EE - 0x61) if 'a' <= c <= 'z' else c for c in t),
    "italic": lambda t: ''.join(chr(ord(c) + 0x1D608 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D622 - 0x61) if 'a' <= c <= 'z' else c for c in t)
}

def random_reply(key): return random.choice(REPLIES.get(key, ["✅ Done"]))
def get_hash_num(text, max_val): return int(hashlib.md5(text.encode()).hexdigest(), 16) % max_val + 1

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
    markup.add("📄 Image→PDF", "🔤 Stylish Font", "🖼️ Sticker", "📦 Zip", "💬 Fake Chat", "🔥 Roast", "💎 Beauty Meter", "💰 Celebrity দাম", "🎲 ভাগ্য গণনা", "🔗 Deep Link", "💸 Fake রিচার্জ", "🐕 কুত্তা Roast")
    bot.send_message(message.chat.id, random_reply("start"), reply_markup=markup)

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    if not state: 
        bot.send_message(chat_id, "আগে /start দিয়ে ফিচার সিলেক্ট করো")
        return
    try:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"/tmp/{chat_id}_{os.path.basename(file_info.file_path)}"
        with open(filename, 'wb') as f: f.write(downloaded)
        if chat_id not in user_files: user_files[chat_id] = []
        user_files[chat_id].append(filename)

        if state == "img2pdf":
            bot.send_message(chat_id, f"✅ {len(user_files[chat_id])}টা নিছি। আরো থাকলে দাও, নাইলে /done লিখো")
        elif state == "sticker":
            img = Image.open(filename).convert("RGBA"); img.thumbnail((512, 512))
            out = f"/tmp/stick_{chat_id}.webp"; img.save(out, "WEBP")
            bot.send_sticker(chat_id, open(out, 'rb')); os.remove(out); cleanup(chat_id)
        elif state == "beauty":
            score = get_hash_num(filename, 100)
            comment = random.choice(BEAUTY_COMMENTS).format(score=score)
            bot.send_photo(chat_id, open(filename, 'rb'), caption=f"💎 **Beauty Meter** 💎\n\n{comment}")
            cleanup(chat_id)
        elif state == "zip":
            bot.send_message(chat_id, f"✅ নিছি। টোটাল: {len(user_files[chat_id])}টা। আরো থাকলে দাও, নাইলে /done")
    except Exception as e: bot.send_message(chat_id, random_reply("error")); cleanup(chat_id)

@bot.message_handler(commands=['done'])
def done_command(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    try:
        if state == "img2pdf" and chat_id in user_files:
            msg = bot.send_message(chat_id, "⏳ PDF বানাচ্ছি...")
            merger = PdfMerger(); pdf_files = []
            for img_path in user_files[chat_id]:
                img = Image.open(img_path).convert('RGB')
                pdf_path = img_path + ".pdf"; img.save(pdf_path); merger.append(pdf_path); pdf_files.append(pdf_path)
            out = f"/tmp/merged_{chat_id}.pdf"; merger.write(out); merger.close()
            bot.send_document(chat_id, open(out, 'rb'), caption="✅ PDF Ready 📄")
            for f in pdf_files: os.remove(f)
            os.remove(out); bot.delete_message(chat_id, msg.message_id)
        elif state == "zip" and chat_id in user_files:
            msg = bot.send_message(chat_id, "⏳ Zip বানাচ্ছি... 📦")
            out = f"/tmp/archive_{chat_id}.zip"
            with zipfile.ZipFile(out, 'w') as zipf:
                for file in user_files[chat_id]: zipf.write(file, os.path.basename(file))
            bot.send_document(chat_id, open(out, 'rb'), caption="✅ Zip Done! 🎁")
            os.remove(out); bot.delete_message(chat_id, msg.message_id)
    except Exception as e: bot.send_message(chat_id, random_reply("error"))
    cleanup(chat_id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
   
