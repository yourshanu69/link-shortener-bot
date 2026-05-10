import os
import telebot
import subprocess
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
    "start": [
        "🔥 বস আসছে! 14টা টুল নিয়ে হাজির। কোনটা চালাবা? 😎",
        "ওই যে! Premium বট রেডি। মজা + কাজ সব হবে 👇",
        "আরে ভাই! Beauty থেকে PDF সব বানায় দিবো। চাপ দাও 💎"
    ],
    "compress_wait": ["⏳ সাইজ কমাচ্ছি... চা খেয়ে আসো ☕", "⏳ ভিডিওটা জিমে পাঠাইছি 💪", "⏳ MB কমাচ্ছি... একটু সবুর 🫡"],
    "compress_done": ["✅ Done! এখন WhatsApp এ যাবে 📤", "✅ ফাইল হালকা! ডাউনলোড করো 📥", "✅ সাইজ কমে গেছে বস 😏"],
    "error": ["❌ উফ! গন্ডগোল। আবার ট্রাই করো 🙏", "❌ Error খাইছি! /start দিয়ে নতুন করে শুরু করো", "❌ কাজ হইলো না ভাই। ফাইল ঠিক আছে?"]
}

ROAST_LINES = [
    "{name} কে দেখলে WiFi ও Password ভুলে যায় 😂",
    "{name} এর মাথায় Google Map ঢুকায় দিলেও রাস্তা খুঁজে পাবে না 🤣",
    "{name} এত Slow, শামুক ওর কাছে হারে 🐌",
    "{name} কে Mirror দেখলে Mirror বলে 'Error 404' 😜",
    "{name} Free Fire খেলে Free তে মরার জন্য 🪂"
]

BEAUTY_COMMENTS = [
    "মাশাল্লাহ! নায়ক/নায়িকা ফেইল 💖 স্কোর: {score}/100",
    "ভাই তুমি তো Filter এর বাপ! Natural Beauty 🔥 স্কোর: {score}/100",
    "এই চেহারা নিয়ে Confidence এর অভাব? চলবে না 😎 স্কোর: {score}/100",
    "10 এ 10! Camera ও লজ্জা পাইছে 📸 স্কোর: {score}/100",
    "ভাই তুমি পাস। কিন্তু আরেকটু ঘুমাইও 😴 স্কোর: {score}/100"
]

CELEB_PRICE = [
    "💰 {name} এর বাজার দর: **{price} কোটি টাকা**! আম্বানি কল দিবে 📞",
    "💎 {name} = **{price} কোটি**! Netflix সিরিজ বানাবে তোমারে নিয়ে 🎬",
    "🏆 {name} এর দাম **{price} কোটি**! তুমি নিজেই একটা Brand 💸"
]

FORTUNE = [
    "🔮 {name}, আগামী মাসে তোমার বিকাশে **{amount} টাকা** আসবে! কিন্তু কষ্ট করতে হবে 💪",
    "🎲 {name}, তোমার ভাগ্যে **{amount} টাকার** লটারি আছে। টিকিট কাটো 🏃",
    "💫 {name}, 2026 সালে তুমি **{amount} টাকার** মালিক হবা। ScreenShot রাখো 📸"
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

def get_hash_num(text, max_val):
    return int(hashlib.md5(text.encode()).hexdigest(), 16) % max_val + 1

@bot.message_handler(commands=['start'])
def start(message):
    cleanup(message.chat.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🗜️ Compress", "📄 Image→PDF", "✂️ Video Cut", "🎵 Video→MP3", "🖼️ Watermark", "🔤 Stylish Font", "🖼️ Sticker", "📦 Zip", "🎭 Prank Voice", "💬 Fake Chat", "🔥 Roast", "💎 Beauty Meter", "💰 Celebrity দাম", "🎲 ভাগ্য গণনা")
    bot.send_message(message.chat.id, random_reply("start"), reply_markup=markup)

@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_files(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    if not state:
        bot.send_message(chat_id, "আগে /start দিয়ে কি করবা সিলেক্ট করো")
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
            bot.send_message(chat_id, f"✅ {len(user_files[chat_id])}টা নিছি। আরো থাকলে দাও, নাইলে /done লিখো") # <-- এই লাইন ঠিক করছি
        elif state == "compress":
            msg = bot.send_message(chat_id, random_reply("compress_wait"))
            out = f"/tmp/comp_{chat_id}.mp4"
            subprocess.run(['ffmpeg', '-i', filename, '-vcodec', 'libx264', '-crf', '28', '-preset', 'fast', out, '-y'], capture_output=True)
            if os.path.exists(out):
                bot.send_document(chat_id, open(out, 'rb'), caption=random_reply("compress_done"))
                os.remove(out)
            bot.delete_message(chat_id, msg.message_id)
            cleanup(chat_id)
        elif state == "sticker":
            img = Image.open(filename).convert("RGBA")
            img.thumbnail((512, 512))
            out = f"/tmp/stick_{chat_id}.webp"
            img.save(out, "WEBP")
            bot.send_sticker(chat_id, open(out, 'rb'))
            os.remove(out); cleanup(chat_id)
        elif state == "vid2aud":
            msg = bot.send_message(chat_id, "⏳ MP3 বানাচ্ছি... 🎵")
            out = f"/tmp/aud_{chat_id}.mp3"
            subprocess.run(['ffmpeg', '-i', filename, '-vn', '-b:a', '192k', out, '-y'], capture_output=True)
            if os.path.exists(out):
                bot.send_audio(chat_id, open(out, 'rb'), title="Converted MP3")
                os.remove(out)
            bot.delete_message(chat_id, msg.message_id)
            cleanup(chat_id)
        elif state == "beauty":
            score = get_hash_num(filename, 100)
            comment = random.choice(BEAUTY_COMMENTS).format(score=score)
            bot.send_photo(chat_id, open(filename, 'rb'), caption=f"💎 **Beauty Meter Result** 💎\n\n{comment}\n\nশেয়ার করে বন্ধুদের জ্বালাও 😂")
            cleanup(chat_id)
        elif state == "watermark":
            user_state[chat_id] = "wm_text"
            bot.send_message(chat_id, "ওকে ফাইল পাইছি। Watermark এ কি লিখবো?")
        elif state == "cut_vid":
            user_state[chat_id] = "cut_time"
            bot.send_message(chat_id, "ভিডিও পাইছি। কত থেকে কত সেকেন্ড কাটবো?\nফরম্যাট: `00:05 00:20`")
        elif state == "zip":
            bot.send_message(chat_id, f"✅ নিছি। টোটাল: {len(user_files[chat_id])}টা। আরো থাকলে দাও, নাইলে /done")

    except Exception as e:
        bot.send_message(chat_id, random_reply("error"))
        cleanup(chat_id)

@bot.message_handler(commands=['done'])
def done_command(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    try:
        if state == "img2pdf" and chat_id in user_files:
            msg = bot.send_message(chat_id, "⏳ PDF বানাচ্ছি...")
            merger = PdfMerger()
            pdf_files = []
            for img_path in user_files[chat_id]:
                img = Image.open(img_path).convert('RGB')
                pdf_path = img_path + ".pdf"; img.save(pdf_path); merger.append(pdf_path); pdf_files.append(pdf_path)
            out = f"/tmp/merged_{chat_id}.pdf"; merger.write(out); merger.close()
            bot.send_document(chat_id, open(out, 'rb'), caption="✅ PDF Ready বস! 📄")
            for f in pdf_files: os.remove(f)
            os.remove(out); bot.delete_message(chat_id, msg.message_id)
        elif state == "zip" and chat_id in user_files:
            msg = bot.send_message(chat_id, "⏳ Zip বানাচ্ছি... 📦")
            out = f"/tmp/archive_{chat_id}.zip"
            with zipfile.ZipFile(out, 'w') as zipf:
                for file in user_files[chat_id]: zipf.write(file, os.path.basename(file))
            bot.send_document(chat_id, open(out, 'rb'), caption="✅ Zip Done! 🎁")
            os.remove(out); bot.delete_message(chat_id, msg.message_id)
    except Exception as e:
        bot.send_message(chat_id, random_reply("error"))
    cleanup(chat_id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    state = user_state.get(chat_id)

    if text == "🗜️ Compress": user_state[chat_id] = "compress"; bot.send_message(chat_id, "ভিডিও/ছবি পাঠাও:"); return
    elif text == "📄 Image→PDF": user_state[chat_id] = "img2pdf"; user_files[chat_id] = []; bot.send_message(chat_id, "ছবিগুলো পাঠাও। শেষ হলে /done"); return
    elif text == "✂️ Video Cut": user_state[chat_id] = "cut_vid"; bot.send_message(chat_id, "ভিডিও পাঠাও:"); return
    elif text == "🎵 Video→MP3": user_state[chat_id] = "vid2aud"; bot.send_message(chat_id, "ভিডিও পাঠাও:"); return
    elif text == "🖼️ Watermark": user_state[chat_id] = "watermark"; bot.send_message(chat_id, "ছবি বা ভিডিও পাঠাও:"); return
    elif text == "🔤 Stylish Font": user_state[chat_id] = "font"; bot.send_message(chat_id, "Normal লেখা দাও:"); return
    elif text == "🖼️ Sticker": user_state[chat_id] = "sticker"; bot.send_message(chat_id, "ছবি পাঠাও:"); return
    elif text == "📦 Zip": user_state[chat_id] = "zip"; user_files[chat_id] = []; bot.send_message(chat_id, "ফাইলগুলো পাঠাও। শেষ হলে /done"); return
    elif text == "🎭 Prank Voice": user_state[chat_id] = "prank"; bot.send_message(chat_id, "Prank এ কি বলবো? লিখো:"); return
    elif text == "💬 Fake Chat": user_state[chat_id] = "fake_name"; bot.send_message(chat_id, "কার নামে Fake Chat? নাম দাও:"); return
    elif text == "🔥 Roast": user_state[chat_id] = "roast"; bot.send_message(chat_id, "🔥 কার ইজ্জতের ফালুদা বানাবো? নাম বলো 😈"); return
    elif text == "💎 Beauty Meter": user_state[chat_id] = "beauty"; bot.send_message(chat_id, "তোমার ছবি পাঠাও। Beauty স্কোর বের করে দেই 💎"); return
    elif text == "💰 Celebrity দাম": user_state[chat_id] = "celeb"; bot.send_message(chat_id, "কার দাম জানতে চাও? নাম লিখো:"); return
    elif text == "🎲 ভাগ্য গণনা": user_state[chat_id] = "fortune"; bot.send_message(chat_id, "নাম আর জন্মসাল দাও। ফরম্যাট: `Sakib 2000`"); return

    try:
        if state == "wm_text":
            filename = user_files[chat_id][0]; out = f"/tmp/wm_{chat_id}.jpg"
            subprocess.run(['ffmpeg', '-i', filename, '-vf', f"drawtext=text='{text}':x=10:y=10:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5", out, '-y'], capture_output=True)
            if os.path.exists(out):
                bot.send_photo(chat_id, open(out, 'rb'), caption="✅ Watermark বসায় দিছি! 😎")
                os.remove(out)
            cleanup(chat_id)
        elif state == "cut_time":
            start_time, end_time = text.split()
            filename = user_files[chat_id][0]; out = f"/tmp/cut_{chat_id}.mp4"
            subprocess.run(['ffmpeg', '-i', filename, '-ss', start_time, '-to', end_time, '-c', 'copy', out, '-y'], capture_output=True)
            if os.path.exists(out):
                bot.send_video(chat_id, open(out, 'rb'), caption=f"✅ কাটছি! {start_time} থেকে {end_time} ✂️")
                os.remove(out)
            cleanup(chat_id)
        elif state == "font":
            result = f"𝗕𝗼𝗹𝗱:\n{FONTS['bold'](text)}\n\n𝘪𝘵𝘢𝘭𝘪𝘤:\n{FONTS['italic'](text)}\n\nকপি করে Bio তে লাগাও 😉"
            bot.send_message(chat_id, result); user_state[chat_id] = None
        elif state == "prank":
            out = f"/tmp/prank_{chat_id}.ogg"
            subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '2', out, '-y'], capture_output=True)
            if os.path.exists(out):
                bot.send_voice(chat_id, open(out, 'rb'), caption=f"🔊 Prank Voice:\n\n“{text}”\n\nবন্ধুকে পাঠাও 😂")
                os.remove(out)
            cleanup(chat_id)
        elif state == "fake_name":
            user_state[chat_id] = "fake_msg"; user_files[chat_id] = [text]
            bot.send_message(chat_id, f"ওকে। `{text}` কি মেসেজ দিবে?", parse_mode="Markdown")
        elif state == "fake_msg":
            name = user_files[chat_id][0]
            img = Image.new('RGB', (450, 150), '#E5DDD5')
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([(10, 10), (440, 140)], 15, fill='white')
            d.text((25, 25), name, fill='#075E54')
            wrapped = textwrap.fill(text, width=40)
            d.text((25, 60), wrapped, fill='black')
            bio = BytesIO(); bio.name = 'fake.png'; img.save(bio, 'PNG'); bio.seek(0)
            bot.send_photo(chat_id, bio, caption="✅ Fake Chat Ready! Meme বানাও 😂")
            cleanup(chat_id)
        elif state == "roast":
            bot.send_message(chat_id, f"🔥 **Roast For {text}:**\n\n{random.choice(ROAST_LINES).format(name=text)}\n\nআরেকটা? 😈")
            user_state[chat_id] = None
        elif state == "celeb":
            price = get_hash_num(text, 500)
            reply = random.choice(CELEB_PRICE).format(name=text, price=price)
            bot.send_message(chat_id, reply)
            user_state[chat_id] = None
        elif state == "fortune":
            parts = text.split()
            name = parts[0]
            amount = get_hash_num(text, 100) * 10000
            reply = random.choice(FORTUNE).format(name=name, amount=amount)
            bot.send_message(chat_id, reply)
            user_state[chat_id] = None
    except Exception as e:
        bot.send_message(chat_id, random_reply("error"))
        cleanup(chat_id)

app = Flask('')
@app.route('/')
def home(): return "Bot is Running"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
bot.infinity_polling()
