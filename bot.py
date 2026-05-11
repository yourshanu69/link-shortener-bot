import os
import telebot
from flask import Flask
from threading import Thread
import random
import zipfile
import textwrap
import hashlib
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telebot import types
from PyPDF2 import PdfMerger
from gtts import gTTS
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
ADMIN_ID = 123456789 # ← @userinfobot থেকে তোমার Telegram ID বসাও
user_state = {}
user_files = {}

# ======== ইউজার Count System ========
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f: json.dump([], f)

def save_user(user_id, username):
    with open(USER_FILE, 'r') as f: users = json.load(f)
    is_new = user_id not in users
    if is_new:
        users.append(user_id)
        with open(USER_FILE, 'w') as f: json.dump(users, f)
        try:
            bot.send_message(ADMIN_ID, f"🔔 নতুন ইউজার: @{username or 'NoUsername'}\nTotal: {len(users)} জন\nTime: {datetime.now().strftime('%d-%m %I:%M %p')}")
        except: pass
    return len(users), is_new

def get_user_count():
    with open(USER_FILE, 'r') as f: return len(json.load(f))
# ===================================

# ======== 64 জেলার লোডশেডিং + ঢাকা থেকে ভাড়া ========
BD_DATA = {
"ঢাকা": {"load": "এলাকা ভিত্তিক", "vara": "Local 10-40 টাকা"},
"গাজীপুর": {"load": "রাত 8-9টা", "vara": "Bus 50 টাকা, Train 45 টাকা"},
"নারায়ণগঞ্জ": {"load": "রাত 9-10টা", "vara": "Bus 35 টাকা, Train 25 টাকা"},
"টাঙ্গাইল": {"load": "রাত 7-8টা", "vara": "Bus 200 টাকা, Train 180 টাকা"},
"কিশোরগঞ্জ": {"load": "রাত 7-8টা", "vara": "Bus 250 টাকা, Train 220 টাকা"},
"মানিকগঞ্জ": {"load": "বিকাল 4-5টা", "vara": "Bus 120 টাকা"},
"মুন্সিগঞ্জ": {"load": "রাত 8-9টা", "vara": "Bus 80 টাকা, Launch 60 টাকা"},
"নরসিংদী": {"load": "রাত 9-10টা", "vara": "Bus 100 টাকা, Train 85 টাকা"},
"ফরিদপুর": {"load": "রাত 8-9টা", "vara": "Bus 300 টাকা"},
"গোপালগঞ্জ": {"load": "রাত 7-8টা", "vara": "Bus 400 টাকা"},
"মাদারীপুর": {"load": "দুপুর 2-3টা", "vara": "Bus 350 টাকা"},
"রাজবাড়ী": {"load": "রাত 9-10টা", "vara": "Bus 320 টাকা"},
"শরীয়তপুর": {"load": "বিকাল 5-6টা", "vara": "Bus 300 টাকা, Launch 250 টাকা"},
"চট্টগ্রাম": {"load": "রাত 9-10টা", "vara": "Bus 480 টাকা, Train 450 টাকা"},
"কক্সবাজার": {"load": "রাত 8-9টা", "vara": "Bus 800 টাকা"},
"রাঙ্গামাটি": {"load": "সকাল 10-11টা", "vara": "Bus 600 টাকা"},
"বান্দরবান": {"load": "দুপুর 2-3টা", "vara": "Bus 620 টাকা"},
"খাগড়াছড়ি": {"load": "রাত 8-9টা", "vara": "Bus 650 টাকা"},
"ফেনী": {"load": "রাত 10-11টা", "vara": "Bus 400 টাকা"},
"নোয়াখালী": {"load": "রাত 8-9টা", "vara": "Bus 400 টাকা"},
"লক্ষ্মীপুর": {"load": "বিকাল 4-5টা", "vara": "Bus 450 টাকা"},
"কুমিল্লা": {"load": "রাত 8-9টা", "vara": "Bus 350 টাকা, Train 345 টাকা"},
"ব্রাহ্মণবাড়িয়া": {"load": "রাত 7-8টা", "vara": "Bus 300 টাকা, Train 280 টাকা"},
"চাঁদপুর": {"load": "রাত 9-10টা", "vara": "Launch 300 টাকা, Bus 350 টাকা"},
"রাজশাহী": {"load": "রাত 7-8টা", "vara": "Bus 500 টাকা, Train 470 টাকা"},
"নাটোর": {"load": "রাত 8-9টা", "vara": "Bus 450 টাকা"},
"নওগাঁ": {"load": "রাত 9-10টা", "vara": "Bus 480 টাকা"},
"চাঁপাইনবাবগঞ্জ": {"load": "বিকাল 5-6টা", "vara": "Bus 520 টাকা"},
"পাবনা": {"load": "রাত 8-9টা", "vara": "Bus 400 টাকা"},
"সিরাজগঞ্জ": {"load": "রাত 7-8টা", "vara": "Bus 350 টাকা"},
"বগুড়া": {"load": "রাত 9-10টা", "vara": "Bus 450 টাকা"},
"জয়পুরহাট": {"load": "রাত 10-11টা", "vara": "Bus 500 টাকা"},
"খুলনা": {"load": "রাত 8-9টা", "vara": "Bus 550 টাকা"},
"বাগেরহাট": {"load": "বিকাল 4-5টা", "vara": "Bus 600 টাকা"},
"সাতক্ষীরা": {"load": "রাত 9-10টা", "vara": "Bus 650 টাকা"},
"যশোর": {"load": "রাত 9-10টা", "vara": "Bus 500 টাকা"},
"ঝিনাইদহ": {"load": "রাত 8-9টা", "vara": "Bus 480 টাকা"},
"মাগুরা": {"load": "দুপুর 2-3টা", "vara": "Bus 450 টাকা"},
"নড়াইল": {"load": "বিকাল 5-6টা", "vara": "Bus 500 টাকা"},
"কুষ্টিয়া": {"load": "রাত 7-8টা", "vara": "Bus 450 টাকা"},
"চুয়াডাঙ্গা": {"load": "রাত 10-11টা", "vara": "Bus 480 টাকা"},
"মেহেরপুর": {"load": "রাত 9-10টা", "vara": "Bus 500 টাকা"},
"বরিশাল": {"load": "রাত 8-9টা", "vara": "Launch 400 টাকা, Bus 500 টাকা"},
"পটুয়াখালী": {"load": "রাত 9-10টা", "vara": "Launch 500 টাকা"},
"ভোলা": {"load": "বিকাল 4-5টা", "vara": "Launch 450 টাকা"},
"পিরোজপুর": {"load": "দুপুর 2-3টা", "vara": "Bus 550 টাকা"},
"বরগুনা": {"load": "রাত 10-11টা", "vara": "Bus 600 টাকা"},
"ঝালকাঠি": {"load": "বিকাল 5-6টা", "vara": "Bus 520 টাকা"},
"সিলেট": {"load": "রাত 9-10টা", "vara": "Bus 550 টাকা, Train 500 টাকা"},
"মৌলভীবাজার": {"load": "রাত 8-9টা", "vara": "Bus 500 টাকা"},
"হবিগঞ্জ": {"load": "রাত 7-8টা", "vara": "Bus 450 টাকা"},
"সুনামগঞ্জ": {"load": "রাত 10-11টা", "vara": "Bus 600 টাকা"},
"রংপুর": {"load": "রাত 8-9টা", "vara": "Bus 600 টাকা, Train 550 টাকা"},
"দিনাজপুর": {"load": "রাত 10-11টা", "vara": "Bus 650 টাকা"},
"কুড়িগ্রাম": {"load": "রাত 9-10টা", "vara": "Bus 700 টাকা"},
"গাইবান্ধা": {"load": "রাত 8-9টা", "vara": "Bus 550 টাকা"},
"নীলফামারী": {"load": "রাত 11-12টা", "vara": "Bus 680 টাকা"},
"লালমনিরহাট": {"load": "রাত 10-11টা", "vara": "Bus 650 টাকা"},
"পঞ্চগড়": {"load": "রাত 9-10টা", "vara": "Bus 750 টাকা"},
"ঠাকুরগাঁও": {"load": "রাত 11-12টা", "vara": "Bus 700 টাকা"},
"ময়মনসিংহ": {"load": "রাত 7-8টা", "vara": "Bus 250 টাকা, Train 220 টাকা"},
"জামালপুর": {"load": "রাত 8-9টা", "vara": "Bus 300 টাকা"},
"শেরপুর": {"load": "রাত 9-10টা", "vara": "Bus 320 টাকা"},
"নেত্রকোণা": {"load": "রাত 10-11টা", "vara": "Bus 280 টাকা"},
}

# ======== Random Reply System ========
REPLIES = {
    "start": [
        "🔥 বস আসছে! Suns Magic 25টা টুল নিয়ে হাজির 😎",
        "ওই যে! Premium বট রেডি। মজা + কাজ সব হবে 👇",
        "Suns Magic চালু! কি লাগবে ভাই? ⚡",
        "স্বাগতম Shakil ভাই! Suns Magic এ সব আছে 🔥"
    ],
    "error": ["❌ উফ! গন্ডগোল। আবার ট্রাই করো 🙏", "❌ Error খাইছি! /start দিয়ে নতুন করে শুরু করো"]
}

DISTRICT_REPLIES = [
    "ভাই কোন জেলার খবর লাগবে? 🤔",
    "64 জেলাই আছে। নাম বলো 😎",
    "জেলা সিলেক্ট করো, লোডশেডিং + ভাড়া বলে দেই 🚌⚡",
    "কোন জেলায় যাবা ভাই? সব তথ্য রেডি 📍"
]

INFO_TEMPLATES = [
    "📍 **{dist}**\n\n⚡ লোডশেডিং: {load}\n🚌 ঢাকা থেকে ভাড়া: {vara}\n\n*আপনাদের সুবিধার্থে সবসময়* ❤️",
    "**{dist} জেলা Update** 🔥\n\nকারেন্ট যাবে: {load}\nবাস ভাড়া: {vara}\n\nআর কিছু লাগবে?",
    "ভাই **{dist}** এর খবর:\n\n🔌 {load}\n💰 {vara}\n\nSafe থাকো ❤️",
    "📊 **{dist}** এর তথ্য:\n\n⚡ Load Shedding: {load}\n🎫 ভাড়া: {vara}\n\nJourney Safe!"
]

NEWS_REPLIES = [
    "📰 **আজকের আপডেট** ({time})\n\n⚡ ঢাকা: রাত 8-11টা 1 ঘন্টা করে লোডশেডিং\n⚡ চট্টগ্রাম: দুপুর 2-5টা শিল্প এলাকায়\n🌧️ বৃষ্টির জন্য গ্রামে কারেন্ট সমস্যা হতে পারে\n\n*Source: DESCO, PDB*",
    "📰 **Power News** ({time})\n\nআজকে Load কম ভাই, টেনশন নাই 😎\n⚡ সিলেট: রাত 9-12টা\n⚡ রংপুর: রাত 8-10টা\n\n*আপডেটেড*",
    "⚡ **ব্রেকিং নিউজ** ({time})\n\nরাজশাহী: সকাল 10-12টা মেইনটেনেন্স\nখুলনা: রাত 9-11টা লোডশেডিং\nবরিশাল: লঞ্চ ঘাট এলাকায় সমস্যা\n\nচার্জ দিয়ে রাখো ভাই 🔋"
]
# ===================================

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
    "10 এ 10! Camera ও লজ্জা পাইছে 📸 স্কোর: {score}/100",
    "ভাই তুমি পাস। কিন্তু আরেকটু ঘুমাইও 😴 স্কোর: {score}/100"
]

CELEB_PRICE = ["💰 {name} এর বাজার দর: **{price} কোটি টাকা**! আম্বানি কল দিবে 📞"]
FORTUNE = ["🔮 {name}, আগামী মাসে তোমার বিকাশে **{amount} টাকা** আসবে! 💪"]
LOVE_CALC = ["❤️ {name1} + {name2} = {percent}% মিল! {result}", "💘 {name1} আর {name2} এর Love স্কোর: {percent}% {result}"]
DICE_ROLL = ["🎲 তুমি পাইছো: **{num}** {emoji}", "🎯 Dice বলতেছে: **{num}** {emoji}"]

FONTS = {
    "bold": lambda t: ''.join(chr(ord(c) + 0x1D5D4 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D5EE - 0x61) if 'a' <= c <= 'z' else c for c in t),
    "italic": lambda t: ''.join(chr(ord(c) + 0x1D608 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D622 - 0x61) if 'a' <= c <= 'z' else c for c in t),
    "mono": lambda t: ''.join(chr(ord(c) + 0x1D670 - 0x41) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D68A - 0x61) if 'a' <= c <= 'z' else c for c in t)
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
    total_users, is_new = save_user(message.from_user.id, message.from_user.username)
    cleanup(message.chat.id)

    # Admin হইলে Total User দেখাবে
    admin_text = f"\n\n📊 **Admin:** Total User {total_users} জন" if message.from_user.id == ADMIN_ID else ""

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📄 Image→PDF", "🔤 Stylish Font", "🖼️ Sticker", "📦 Zip", "💬 Fake Chat",
               "🔥 Roast", "💎 Beauty Meter", "💰 Celebrity দাম", "🎲 ভাগ্য গণনা", "🔗 Deep Link",
               "💸 Fake রিচার্জ", "🐕 কুত্তা Roast", "🎭 Prank Voice", "❤️ Love ক্যালকুলেটর", "🎯 Dice রোল",
               "🪞 উল্টা লেখা", "🔢 নাম্বার গেস", "😂 জোকস", "🧮 ক্যালকুলেটর", "📢 Announcement")
    markup.add("🇧🇩 64 জেলা তথ্য", "📰 কারেন্ট নিউজ", "👤 Shakil Ahmed Shanu", "🎵 শুনতে চাইলে ক্লিক", "📞 Contact Admin")
    bot.send_message(message.chat.id, random_reply("start") + admin_text, reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id == ADMIN_ID:
        count = get_user_count()
        bot.send_message(message.chat.id, f"📊 **Suns Magic Stats**\n\nTotal User: {count} জন\n\n*আপনাদের সুবিধার্থে সবসময়*")
    else:
        bot.send_message(message.chat.id, "এইটা Admin Command ভাই 😅")

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
    cleanup(chat_id); start(message)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    state = user_state.get(chat_id)

    # ======== 20টা পুরান অপশন ========
    if text == "📄 Image→PDF": user_state[chat_id] = "img2pdf"; user_files[chat_id] = []; bot.send_message(chat_id, "ছবিগুলো পাঠাও। শেষ হলে /done"); return
    elif text == "🔤 Stylish Font": user_state[chat_id] = "font"; bot.send_message(chat_id, "Normal লেখা দাও:"); return
    elif text == "🖼️ Sticker": user_state[chat_id] = "sticker"; bot.send_message(chat_id, "ছবি পাঠাও:"); return
    elif text == "📦 Zip": user_state[chat_id] = "zip"; user_files[chat_id] = []; bot.send_message(chat_id, "ফাইলগুলো পাঠাও। শেষ হলে /done"); return
    elif text == "💬 Fake Chat": user_state[chat_id] = "fake_name"; bot.send_message(chat_id, "কার নামে Fake Chat? নাম দাও:"); return
    elif text == "🔥 Roast": user_state[chat_id] = "roast"; bot.send_message(chat_id, "🔥 কার ইজ্জতের ফালুদা বানাবো? নাম বলো 😈"); return
    elif text == "💎 Beauty Meter": user_state[chat_id] = "beauty"; bot.send_message(chat_id, "তোমার ছবি পাঠাও 💎"); return
    elif text == "💰 Celebrity দাম": user_state[chat_id] = "celeb"; bot.send_message(chat_id, "কার দাম জানতে চাও? নাম লিখো:"); return
    elif text == "🎲 ভাগ্য গণনা": user_state[chat_id] = "fortune"; bot.send_message(chat_id, "নাম আর জন্মসাল দাও। ফরম্যাট: `Sakib 2000`"); return
    elif text == "🔗 Deep Link": user_state[chat_id] = "deep_link"; bot.send_message(chat_id, "Deep Link এ কি Code বসাবা? যেমন: `ref_sakib`"); return
    elif text == "💸 Fake রিচার্জ": user_state[chat_id] = "recharge_num"; bot.send_message(chat_id, "কার নাম্বারে রিচার্জ দেখাবা? নাম্বার দাও: 01XXXXXXXXX"); return
    elif text == "🐕 কুত্তা Roast": user_state[chat_id] = "kutta_roast"; bot.send_message(chat_id, "🐕 কোন কুত্তার নামে Roast শুনবা? নাম বলো 😈"); return
    elif text == "❤️ Love ক্যালকুলেটর": user_state[chat_id] = "love"; bot.send_message(chat_id, "দুইজনের নাম দাও। ফরম্যাট: `Sakib + Nusrat`"); return
    elif text == "🎯 Dice রোল": roll_dice(chat_id); return
    elif text == "🪞 উল্টা লেখা": user_state[chat_id] = "reverse"; bot.send_message(chat_id, "যে লেখা উল্টাবা সেটা দাও:"); return
    elif text == "🔢 নাম্বার গেস": user_state[chat_id] = "guess_num"; user_files[chat_id] = [random.randint(1,100)]; bot.send_message(chat_id, "আমি 1-100 এর মধ্যে একটা নাম্বার ভাবছি। গেস করো:"); return
    elif text == "😂 জোকস": send_joke(chat_id); return
    elif text == "🧮 ক্যালকুলেটর": user_state[chat_id] = "calc"; bot.send_message(chat_id, "হিসাব লিখো। যেমন: `50 + 20 * 2`"); return
    elif text == "📢 Announcement": user_state[chat_id] = "announce"; bot.send_message(chat_id, "Announcement এ কি লিখবা? বড় করে ব্যানার বানায় দিবো:"); return
    elif text == "🎭 Prank Voice":
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("👨 ছেলে Voice", "👩 মেয়ে Voice", "⬅️ Back")
        user_state[chat_id] = "prank_gender"
        bot.send_message(chat_id, "Prank এ কোন Voice দিবো? সিলেক্ট করো:", reply_markup=markup)
        return

    # ======== নতুন 5টা অপশন ========
    elif text == "🇧🇩 64 জেলা তথ্য":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        btns = [types.KeyboardButton(dist) for dist in BD_DATA.keys()]
        btns.append(types.KeyboardButton("⬅️ Menu"))
        markup.add(*btns)
        bot.send_message(chat_id, random.choice(DISTRICT_REPLIES), reply_markup=markup)
        return

    elif text == "📰 কারেন্ট নিউজ":
        news = random.choice(NEWS_REPLIES).format(time=datetime.now().strftime('%I:%M %p'))
        bot.send_message(chat_id, news)
        return

    elif text == "👤 Shakil Ahmed Shanu":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔊 20 বছরের Shakil এর Voice শুনো", callback_data="play_shanu_voice"))
        bot.send_message(chat_id, "👤 **Shakil Ahmed Shanu**\n\n🎂 বয়স: 20 বছর\n📍 Owner: Suns Magic Bot\n\nনিচে ক্লিক করে Voice শুনো 👇", reply_markup=markup)
        return

    elif text == "🎵 শুনতে চাইলে ক্লিক":
        send_shanu_voice(chat_id)
        return

    elif text == "📞 Contact Admin":
        bot.send_message(chat_id, f"📞 **Admin Contact**\n\n👤 Name: Shakil Ahmed Shanu\n🆔 Telegram: @ShakilAhmedShanu\n📱 User ID: `{ADMIN_ID}`\n\nযেকোনো সমস্যায় Message দাও ❤️", parse_mode="Markdown")
        return

    elif text == "⬅️ Menu":
        start(message)
        return

    elif text in BD_DATA.keys():
        dist = text
        data = BD_DATA
        reply = random.choice(INFO_TEMPLATES).format(dist=dist, load=data['load'], vara=data['vara'])
        bot.send_message(chat_id, reply)
        return

    elif text == "⬅️ Back":
        start(message)
        return

    try:
        if state == "font":
            result = f"𝗕𝗼𝗹𝗱:\n{FONTS['bold'](text)}\n\n𝘪𝘵𝘢𝘭𝘪𝘤:\n{FONTS['italic'](text)}\n\n𝙼𝚘𝚗𝚘:\n{FONTS['mono'](text)}\n\nকপি করে Bio তে লাগাও 😉"
            bot.send_message(chat_id, result); user_state[chat_id] = None; start(message)
        elif state == "fake_name":
            user_state[chat_id] = "fake_msg"; user_files[chat_id] = [text]
            bot.send_message(chat_id, f"ওকে। `{text}` কি মেসেজ দিবে?", parse_mode="Markdown")
        elif state == "fake_msg":
            name = user_files[chat_id][0]
            img = Image.new('RGB', (450, 150), '#E5DDD5'); d = ImageDraw.Draw(img)
                    elif state.startswith("prank_👦") or state.startswith("prank_👨") or state.startswith("prank_👴") or state.startswith("prank_👧") or state.startswith("prank_👩") or state.startswith("prank_👵"):
            msg = bot.send_message(chat_id, "⏳ Voice বানাচ্ছি... 🎙️ লম্বা লাইন হলে 10-15 সেকেন্ড লাগবে")
            try:
                is_male = "👦" in state or "👨" in state or "👴" in state
                is_slow = "বাচ্চা" in state or "বুড়া" in state or "বুড়ি" in state
                        elif state == "font":
            fonts = {"bold": "**{}**", "italic": "__{}__", "mono": "`{}`", "strike": "~~{}~~", "bubble": "ⓑⓤⓑⓛⓔ"}
            styled = "\n\n".join([f"{name.title()}:\n{style.format(text)}" for name, style in fonts.items()])
            bot.send_message(chat_id, f"✅ **Stylish Font Ready:**\n\n{styled}")
            user_state[chat_id] = None; start(message)
        elif state.startswith("prank_"):
            msg = bot.send_message(chat_id, "⏳ Voice বানাচ্ছি... 🎙️ লম্বা লাইন হলে 10-15 সেকেন্ড লাগবে")
            try:
                is_male = "👦" in state or "👨" in state or "👴" in state
                is_slow = "বাচ্চা" in state or "বুড়া" in state or "বুড়ি" in state
                tld = 'com.au' if is_male else 'co.in'
                tts = gTTS(text=text, lang='bn', tld=tld, slow=is_slow)
                out = f"/tmp/prank_{chat_id}.mp3"
                tts.save(out)
                caption = f"🔊 {state.replace('prank_','')} Prank Voice:\n\n“{text}”\n\nবন্ধুকে পাঠাও 😂"
                bot.send_voice(chat_id, open(out, 'rb'), caption=caption)
                os.remove(out)
            except Exception as e:
                bot.send_message(chat_id, "❌ Voice বানাতে পারলাম না। 500 অক্ষরের বেশি দিও না।")
            bot.delete_message(chat_id, msg.message_id)
            cleanup(chat_id); start(message)
        elif state == "deep_link":
            bot_username = bot.get_me().username
            link = f"https://t.me/{bot_username}?start={text}"
            bot.send_message(chat_id, f"✅ **Deep Link Ready:**\n\n`{link}`\n\nশেয়ার করো 🔗")
            user_state[chat_id] = None; start(message)
        elif state == "recharge_num":
            user_state[chat_id] = "recharge_amount"; user_files[chat_id] = [text]
            bot.send_message(chat_id, f"ওকে {text} নাম্বারে কত টাকা রিচার্জ? যেমন: 500")
