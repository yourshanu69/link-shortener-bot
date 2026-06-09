import os
from flask import Flask, request
import telebot
from PIL import Image, ImageEnhance
from io import BytesIO
import requests
import random
import datetime
import asyncio
import nest_asyncio
nest_asyncio.apply()
import json

import telebot
from telebot import types
from flask import Flask, request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import edge_tts

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
RENDER_URL = os.environ.get('RENDER_URL')

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}

# ========== ইউজার ডাটাবেস + নোটিফিকেশন ==========
ADMIN_ID = 1692907487 # <-- তোমার Telegram ID বসাও এখানে

DB_FILE = "/tmp/user_db.json"
user_db = {}

def load_users():
    global user_db
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            user_db = json.load(f)

def save_users():
    with open(DB_FILE, 'w') as f:
        json.dump(user_db, f)

load_users()

def notify_admin(text):
    try:
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except:
        pass
# ==============================================

# Vocabulary লোড
vocab_list = []
file_path = os.path.join(os.path.dirname(__file__), 'vocab.txt')
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                if len(parts) == 3:
                    word, meaning, example = parts
                    vocab_list.append({"word": word, "meaning": meaning, "example": example})
    print(f"Vocab লোড হইছে: {len(vocab_list)} টা ওয়ার্ড")
except Exception as e:
    print(f"vocab.txt এরর: {e}")

# Font download
def download_font():
    font_path = "/tmp/NotoSansBengali.ttf"
    if not os.path.exists(font_path) or os.path.getsize(font_path) < 100000:
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf"
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
    return font_path

FONT_PATH = download_font()
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bengali', FONT_PATH))

tools = {
    'fun': "🎭 Fun Zone",
    'txt_pdf': "📝 টেক্সট → PDF",
    'img_pdf': "📄 ছবি → PDF",
    'qr': "🔗 QR কোড",
    'blur': "🌫️ ব্লার",
    'resize': "📏 রিসাইজ",
    'textimg': "✍️ টেক্সট → ছবি",
    'age': "🎂 Age Calculator",
    'word': "📊 Word Counter",
    'meme': "😂 মিম বানাও",
    'compress': "🗜️ ছবি কমপ্রেস",
    'removebg': "✂️ BG রিমুভ",
    'ip': "🌐 IP Lookup",
    'weather': "🌤️ Weather",
    'bright': "☀️ ব্রাইটনেস",
    'female_tts': "🎤 BD Female Voice",
    'male_tts': "🎤 BD Male Voice"
}

@app.route('/', methods=['GET'])
def home():
    return "Shanu's Magic Bot v6.2 - 17 Tools + Stats 🔥"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

def cancel_prev(chat_id):
    if user_state.get(chat_id):
        user_state[chat_id] = None
        bot.send_message(chat_id, "ক্যান্সেল হলো ✅")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    month = datetime.datetime.now().strftime("%Y-%m")

    is_new = False
    # নতুন ইউজার হলে সেভ + এডমিনকে নোটিফাই
    if user_id not in user_db:
        is_new = True
        user_db[user_id] = {
            "first_seen": today,
            "last_seen": today,
            "month": month,
            "username": message.from_user.username or message.from_user.first_name
        }
        notify_admin(f"🎉 **নতুন ইউজার জয়েন করছে!**\n\nID: `{user_id}`\nনাম: {user_db[user_id]['username']}\nমোট ইউজার: {len(user_db)} জন")
    else:
        user_db[user_id]["last_seen"] = today
        user_db[user_id]["month"] = month

    save_users()

    cancel_prev(message.chat.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(v) for v in tools.values()])
    welcome = "🔥 **Shanu's Magic Bot v6.2**\n17টা টুল রেডি। সব ফ্রি + ফাস্ট\n`/cancel` দিয়ে বাতিল করো\n`/stats` দিলে বটের স্ট্যাটস দেখতে পারবা" if message.chat.id == ADMIN_ID else "🔥 **Shanu's Magic Bot v6.2**\n17টা টুল রেডি। সব ফ্রি + ফাস্ট\n`/cancel` দিয়ে বাতিল করো"
    bot.send_message(message.chat.id, welcome, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    cancel_prev(message.chat.id)

# ========== Admin Stats Command ==========
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id!= ADMIN_ID:
        bot.send_message(message.chat.id, "❌ তোমার পারমিশন নাই ভাই")
        return

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    month = datetime.datetime.now().strftime("%Y-%m")

    total_users = len(user_db)
    today_users = len([u for u in user_db.values() if u.get("last_seen") == today])
    month_users = len([u for u in user_db.values() if u.get("month") == month])

    text = f"""📊 **বট স্ট্যাটস**

👥 মোট ইউজার: {total_users} জন
📅 আজকে একটিভ: {today_users} জন
🗓️ এই মাসে: {month_users} জন

🚀 বট তো ভাইরাল হয়ে যাইতেছে!"""

    bot.send_message(message.chat.id, text, parse_mode="Markdown")
# ========================================

# 1. Fun Zone
@bot.message_handler(func=lambda m: m.text == "🎭 Fun Zone")
def fun_zone(message):
    cancel_prev(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('😂 জোকস', '🎲 রিডল', '📚 ফ্যাক্ট', '🔙 ব্যাক')
    bot.send_message(message.chat.id, "🎭 Fun Zone:", reply_markup=markup)
    user_state[message.chat.id] = 'fun_menu'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'fun_menu')
def fun_handler(message):
    jokes = ["শিক্ষক: 2+2=? ছাত্র: 22 স্যার! 😂", "কম্পিউটার: আমি হ্যাং। ইউজার: আমিও!"]
    riddles = ["4 পা আছে কিন্তু হাঁটতে পারি না। কে? উত্তর: টেবিল"]
    facts = ["পৃথিবীর সবচেয়ে বড় মরুভূমি সাহারা", "অক্টোপাসের 3টা হার্ট আছে"]
    txt = message.text.lower()
    if 'জোকস' in txt:
        bot.send_message(message.chat.id, random.choice(jokes))
    elif 'রিডল' in txt:
        bot.send_message(message.chat.id, random.choice(riddles))
    elif 'ফ্যাক্ট' in txt:
        bot.send_message(message.chat.id, random.choice(facts))
    elif 'ব্যাক' in txt:
        start(message)
        return
    user_state[message.chat.id] = None

# 2. Text → PDF
@bot.message_handler(func=lambda m: m.text == "📝 টেক্সট → PDF")
def txt_pdf_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'txt_pdf'
    bot.send_message(message.chat.id, "📝 PDF এ যেটা লিখতে চাও সেটা পাঠাও\nবাংলা + ইংলিশ দুইটাই লিখতে পারবা")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'txt_pdf')
def txt_pdf_process(message):
    try:
        c = canvas.Canvas("/tmp/text.pdf", pagesize=A4)
        width, height = A4
        c.setFont('Bengali', 14)
        y = height - 50
        max_width = width - 100
        for line in message.text.split('\n'):
            wrapped_lines = simpleSplit(line, 'Bengali', 14, max_width)
            for wrapped in wrapped_lines:
                c.drawString(50, y, wrapped)
                y -= 25
                if y < 50:
                    c.showPage()
                    c.setFont('Bengali', 14)
                    y = height - 50
        c.save()
        with open('/tmp/text.pdf', 'rb') as f:
            bot.send_document(message.chat.id, f, caption="✅ PDF রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 3. Image → PDF
@bot.message_handler(func=lambda m: m.text == "📄 ছবি → PDF")
def pdf_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = {'state': 'pdf', 'images': []}
    bot.send_message(message.chat.id, "📷 ছবি পাঠাও। শেষে 'Done' লিখো")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'pdf', content_types=['photo', 'text'])
def pdf_process(message):
    if message.text and 'done' in message.text.lower():
        if not user_state[message.chat.id]['images']:
            bot.send_message(message.chat.id, "কোনো ছবি নাই")
            user_state[message.chat.id] = None
            return
        try:
            imgs = [Image.open(BytesIO(i)).convert('RGB') for i in user_state[message.chat.id]['images']]
            imgs[0].save('/tmp/output.pdf', save_all=True, append_images=imgs[1:])
            with open('/tmp/output.pdf', 'rb') as f:
                bot.send_document(message.chat.id, f, caption="✅ PDF রেডি")
            user_state[message.chat.id] = None
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        return
    if message.photo:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        user_state[message.chat.id]['images'].append(downloaded)
        bot.send_message(message.chat.id, f"✅ {len(user_state[message.chat.id]['images'])} টা ছবি যোগ হলো")

# 4. QR Generator
@bot.message_handler(func=lambda m: m.text == "🔗 QR কোড")
def qr_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'qr'
    bot.send_message(message.chat.id, "🔗 লিংক বা টেক্সট লিখো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'qr')
def qr_process(message):
    try:
        qr = qrcode.QRCode(box_size=10, border=5)
        qr.add_data(message.text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ QR রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 5. BG Blur
@bot.message_handler(func=lambda m: m.text == "🌫️ ব্লার")
def blur_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'blur'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'blur', content_types=['photo'])
def blur_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded)).filter(ImageFilter.GaussianBlur(15))
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ ব্লার কমপ্লিট!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 6. Resize Image
@bot.message_handler(func=lambda m: m.text == "📏 রিসাইজ")
def resize_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'resize'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'resize', content_types=['photo'])
def resize_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded)).resize((800, 800))
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ 800x800 তে রিসাইজ হলো!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 7. Text to Image
@bot.message_handler(func=lambda m: m.text == "✍️ টেক্সট → ছবি")
def textimg_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'textimg'
    bot.send_message(message.chat.id, "✍️ ছবিতে কী লিখবে লিখো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'textimg')
def textimg_process(message):
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
        img = Image.new('RGB', (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((400, 200), message.text, fill=(0,0,0), anchor="mm", font=font)
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ ছবি রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 8. Age Calculator
@bot.message_handler(func=lambda m: m.text == "🎂 Age Calculator")
def age_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'age'
    bot.send_message(message.chat.id, "🎂 জন্ম তারিখ লিখো: YYYY-MM-DD\nউদাহরণ: 2000-05-15")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'age')
def age_process(message):
    try:
        birth = datetime.datetime.strptime(message.text, "%Y-%m-%d")
        today = datetime.datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        bot.send_message(message.chat.id, f"🎂 তোমার বয়স: {age} বছর")
        user_state[message.chat.id] = None
    except:
        bot.send_message(message.chat.id, "❌ ফরম্যাট ভুল। YYYY-MM-DD লিখো")

# 9. Word Counter
@bot.message_handler(func=lambda m: m.text == "📊 Word Counter")
def word_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'word'
    bot.send_message(message.chat.id, "📊 টেক্সট পাঠাও, শব্দ গুনে দিবো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'word')
def word_process(message):
    words = len(message.text.split())
    chars = len(message.text)
    bot.send_message(message.chat.id, f"📊 মোট শব্দ: {words}\nমোট ক্যারেক্টার: {chars}")
    user_state[message.chat.id] = None

# 10. Meme Maker
@bot.message_handler(func=lambda m: m.text == "😂 মিম বানাও")
def meme_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = {'state': 'meme_img'}
    bot.send_message(message.chat.id, "📷 মিমের জন্য ছবি পাঠাও")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'meme_img', content_types=['photo'])
def meme_img(message):
    downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    user_state[message.chat.id]['img'] = downloaded
    user_state[message.chat.id]['state'] = 'meme_text'
    bot.send_message(message.chat.id, "✍️ লিখো: `উপরের টেক্সট | নিচের টেক্সট`")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'meme_text')
def meme_text(message):
    try:
        text = message.text.split('|')
        top = text[0].strip() if len(text) > 0 else ""
        bottom = text[1].strip() if len(text) > 1 else ""
        font = ImageFont.truetype(FONT_PATH, 45)
        img = Image.open(BytesIO(user_state[message.chat.id]['img'])).convert('RGB')
        draw = ImageDraw.Draw(img)
        w, h = img.size
        if top:
            draw.text((w//2, 50), top.upper(), fill="white", anchor="mm", font=font, stroke_width=2, stroke_fill="black")
        if bottom:
            draw.text((w//2, h-50), bottom.upper(), fill="white", anchor="mm", font=font, stroke_width=2, stroke_fill="black")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ মিম রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 11. Compress Image
@bot.message_handler(func=lambda m: m.text == "🗜️ ছবি কমপ্রেস")
def compress_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'compress'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও, সাইজ কমায় দিবো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'compress', content_types=['photo'])
def compress_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded))
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=60, optimize=True)
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ 60% কমপ্রেস হলো!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 12. Remove BG
@bot.message_handler(func=lambda m: m.text == "✂️ BG রিমুভ")
def removebg_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'removebg'
    bot.send_message(message.chat.id, "🖼️ সলিড ব্যাকগ্রাউন্ডের ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'removebg', content_types=['photo'])
def removebg_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded)).convert('RGBA')
        datas = img.getdata()
        newData = [(255,255,255,0) if item[0]>240 and item[1]>240 and item[2]>240 else item for item in datas]
        img.putdata(newData)
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ BG রিমুভ হলো!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 13. IP Lookup
@bot.message_handler(func=lambda m: m.text == "🌐 IP Lookup")
def ip_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'ip'
    bot.send_message(message.chat.id, "🌐 IP বা ডোমেইন লিখো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'ip')
def ip_process(message):
    try:
        r = requests.get(f"http://ip-api.com/json/{message.text}", timeout=5)
        data = r.json()
        if data['status'] == 'success':
            txt = f"🌐 **IP Info**\n\nIP: {data['query']}\nCountry: {data['country']}\nCity: {data['city']}\nISP: {data['isp']}"
            bot.send_message(message.chat.id, txt, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ IP পাওয়া যায়নি")
        user_state[message.chat.id] = None
    except:
        bot.send_message(message.chat.id, "❌ এরর হয়েছে")

# 14. Weather
@bot.message_handler(func=lambda m: m.text == "🌤️ Weather")
def weather_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'weather'
    bot.send_message(message.chat.id, "🌤️ শহরের নাম লিখো। যেমন: Dhaka")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'weather')
def weather_process(message):
    try:
        r = requests.get(f"https://wttr.in/{message.text}?format=3&lang=bn", timeout=5)
        bot.send_message(message.chat.id, r.text)
        user_state[message.chat.id] = None
    except:
        bot.send_message(message.chat.id, "❌ শহর খুঁজে পাইনি")

# 15. Brightness
@bot.message_handler(func=lambda m: m.text == "☀️ ব্রাইটনেস")
def bright_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'bright'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'bright', content_types=['photo'])
def bright_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded))
        img = ImageEnhance.Brightness(img).enhance(1.5)
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ ব্রাইটনেস বাড়ানো হলো!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return "ok", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get('RENDER_EXTERNAL_URL') + '/webhook')
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
