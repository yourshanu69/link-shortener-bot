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
from gtts import gTTS

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
user_files = {}

REPLIES = {
    "start": ["🔥 বস আসছে! 20টা টুল নিয়ে হাজির 😎", "ওই যে! Premium বট রেডি। মজা + কাজ সব হবে 👇"],
    "error": ["❌ উফ! গন্ডগোল। আবার ট্রাই করো 🙏", "❌ Error খাইছি! /start দিয়ে নতুন করে শুরু করো"]
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
    cleanup(message.chat.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📄 Image→PDF", "🔤 Stylish Font", "🖼️ Sticker", "📦 Zip", "💬 Fake Chat", 
               "🔥 Roast", "💎 Beauty Meter", "💰 Celebrity দাম", "🎲 ভাগ্য গণনা", "🔗 Deep Link", 
               "💸 Fake রিচার্জ", "🐕 কুত্তা Roast", "🎭 Prank Voice", "❤️ Love ক্যালকুলেটর", "🎯 Dice রোল",
               "🪞 উল্টা লেখা", "🔢 নাম্বার গেস", "😂 জোকস", "🧮 ক্যালকুলেটর", "📢 Announcement")
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
    cleanup(chat_id); start(message)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    state = user_state.get(chat_id)

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
            d.rounded_rectangle([(10, 10), (440, 140)], 15, fill='white')
            d.text((25, 25), name, fill='#075E54'); wrapped = textwrap.fill(text, width=40); d.text((25, 60), wrapped, fill='black')
            bio = BytesIO(); bio.name = 'fake.png'; img.save(bio, 'PNG'); bio.seek(0)
            bot.send_photo(chat_id, bio, caption="✅ Fake Chat Ready! 😂"); cleanup(chat_id); start(message)
        elif state == "roast":
            bot.send_message(chat_id, f"🔥 **Roast For {text}:**\n\n{random.choice(ROAST_LINES).format(name=text)}")
            user_state[chat_id] = None; start(message)
        elif state == "kutta_roast":
            bot.send_message(chat_id, f"🐕 **কুত্তা Roast:**\n\n{random.choice(KUTTA_ROAST).format(name=text)}")
            user_state[chat_id] = None; start(message)
        elif state == "celeb":
            price = get_hash_num(text, 500)
            bot.send_message(chat_id, random.choice(CELEB_PRICE).format(name=text, price=price))
            user_state[chat_id] = None; start(message)
        elif state == "fortune":
            name = text.split()[0]; amount = get_hash_num(text, 100) * 10000
            bot.send_message(chat_id, random.choice(FORTUNE).format(name=name, amount=amount))
            user_state[chat_id] = None; start(message)
        elif state == "deep_link":
            bot_username = bot.get_me().username
            link = f"https://t.me/{bot_username}?start={text}"
            bot.send_message(chat_id, f"✅ **Deep Link Ready:**\n\n`{link}`\n\nশেয়ার করো 🔗")
            user_state[chat_id] = None; start(message)
        elif state == "recharge_num":
            user_state[chat_id] = "recharge_amount"; user_files[chat_id] = [text]
            bot.send_message(chat_id, f"ওকে {text} নাম্বারে কত টাকা রিচার্জ? যেমন: 500")
        elif state == "recharge_amount":
            number = user_files[chat_id][0]; amount = text
            img = Image.new('RGB', (400, 600), '#FFFFFF'); d = ImageDraw.Draw(img)
            d.rectangle([(0, 0), (400, 80)], fill='#E2136E')
            d.text((120, 25), "bKash", fill='white')
            d.text((30, 120), "Recharge Successful!", fill='#00AA00')
            d.text((30, 180), f"Number: {number}", fill='black')
            d.text((30, 220), f"Amount: ৳{amount}", fill='black')
            d.text((30, 260), f"TrxID: TX{random.randint(10000000,99999999)}", fill='gray')
            d.text((30, 320), "বন্ধুকে পাঠায় দাও 😂", fill='#E2136E')
            bio = BytesIO(); bio.name = 'recharge.png'; img.save(bio, 'PNG'); bio.seek(0)
            bot.send_photo(chat_id, bio, caption="✅ Fake রিচার্জ Ready! 💸"); cleanup(chat_id); start(message)
        elif state == "love":
            names = text.split('+'); name1, name2 = names[0].strip(), names[1].strip()
            percent = get_hash_num(text, 100)
            result = "Perfect Juti! 💍" if percent > 80 else "চেষ্টা করলে হবে 💪" if percent > 50 else "বন্ধু হয়েই থাকো 😅"
            bot.send_message(chat_id, random.choice(LOVE_CALC).format(name1=name1, name2=name2, percent=percent, result=result))
            user_state[chat_id] = None; start(message)
        elif state == "reverse":
            bot.send_message(chat_id, f"🪞 উল্টা লেখা:\n\n`{text[::-1]}`", parse_mode="Markdown")
            user_state[chat_id] = None; start(message)
        elif state == "guess_num":
            correct = user_files[chat_id][0]
            guess = int(text)
            if guess == correct: bot.send_message(chat_id, f"🎉 জিতছো! নাম্বার ছিল {correct}")
            elif guess < correct: bot.send_message(chat_id, "📈 আরো বড় নাম্বার বলো")
            else: bot.send_message(chat_id, "📉 আরো ছোট নাম্বার বলো")
            if guess == correct: cleanup(chat_id); start(message)
        elif state == "calc":
            try:
                result = eval(text.replace('x','*').replace('÷','/'))
                bot.send_message(chat_id, f"🧮 রেজাল্ট: `{text} = {result}`", parse_mode="Markdown")
            except: bot.send_message(chat_id, "❌ হিসাব ভুল। আবার দাও")
            user_state[chat_id] = None; start(message)
        elif state == "announce":
            img = Image.new('RGB', (600, 300), '#FF0000'); d = ImageDraw.Draw(img)
            d.rectangle([(10, 10), (590, 290)], outline='yellow', width=5)
            wrapped = textwrap.fill(text, width=20)
            d.text((300, 150), wrapped, fill='white', anchor="mm", align="center")
            bio = BytesIO(); bio.name = 'announce.png'; img.save(bio, 'PNG'); bio.seek(0)
            bot.send_photo(chat_id, bio, caption="📢 Announcement Ready!"); cleanup(chat_id); start(message)
        elif state == "prank_gender":
            if text == "👨 ছেলে Voice":
                markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                markup.add("👦 বাচ্চা", "👨 যুবক", "👴 বুড়া", "⬅️ Back")
                user_state[chat_id] = "prank_male_age"
                bot.send_message(chat_id, "ছেলের বয়স কত? সিলেক্ট করো:", reply_markup=markup)
            elif text == "👩 মেয়ে Voice":
                markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                markup.add("👧 বাচ্চা", "👩 যুবতী", "👵 বুড়ি", "⬅️ Back")
                user_state[chat_id] = "prank_female_age"
                bot.send_message(chat_id, "মেয়ের বয়স কত? সিলেক্ট করো:", reply_markup=markup)
            else: start(message)
        elif state == "prank_male_age" or state == "prank_female_age":
            user_state[chat_id] = f"prank_{text}" # prank_👦 বাচ্চা
            bot.send_message(chat_id, "ওকে। এখন Prank এ কি বলবো? লম্বা করে লিখো:", reply_markup=types.ReplyKeyboardRemove())
        elif state.startswith("prank_👦") or state.startswith("prank_👨") or state.startswith("prank_👴") or state.startswith("prank_👧") or state.startswith("prank_👩") or state.startswith("prank_👵"):
            msg = bot.send_message(chat_id, "⏳ Voice বানাচ্ছি... 🎙️ লম্বা লাইন হলে 10-15 সেকেন্ড লাগবে")
            try:
                # ছেলে = com.au, মেয়ে = co.in, বাচ্চা = slow=True, বুড়া = slow=True
                is_male = "👦" in state or "👨" in state or "👴" in state
                is_slow = "👦" in state or "👴" in state or "👧" in state or "👵" in state
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
    except Exception as e: bot.send_message(chat_id, random_reply("error")); cleanup(chat_id); start(message)

def roll_dice(chat_id):
    num = random.randint(1,6)
    emoji = "🎯" if num == 6 else "🎲"
    bot.send_message(chat_id, random.choice(DICE_ROLL).format(num=num, emoji=emoji))

def send_joke(chat_id):
    jokes = [
        "শিক্ষক: বলতো, পানির ফর্মুলা কি?\nছাত্র: H2O\nশিক্ষক: Good! H2O মানে কি?\nছাত্র: স্যার... H=হালকা, 2=দুই, O=আউন্স 😂",
        "ডাক্তার: আপনার রিপোর্ট দেখে মনে হচ্ছে আপনি খুব টেনশনে থাকেন।\nরোগী: না স্যার, আমি টেনশন নিই না।\nডাক্তার: তাহলে এত চুল পাকলো কিভাবে?\nরোগী: স্যার, ওটা তো বউ এর টেনশনে 😭",
        "বউ: তুমি আমাকে ভালোবাসো?\nজামাই: হ্যাঁ, নিজের থেকেও বেশি।\nবউ: তাহলে আমার জন্য মরতে পারবা?\nজামাই: তোমার জন্য মরলে তো তোমাকেই হারাবো 😎"
    ]
    bot.send_message(chat_id, f"😂 **জোকস:**\n\n{random.choice(jokes)}")

app = Flask('')
@app.route('/')
def home(): return "Bot is Running"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
bot.infinity_polling()
