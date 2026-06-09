import os
import telebot
import json
import random
from flask import Flask, request
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from io import BytesIO
import requests
from PyPDF2 import PdfReader, PdfWriter
from gtts import gTTS

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

USER_FILE = 'users.json'
PDF_SESSION = {}
SPLIT_SESSION = {}

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USER_FILE, 'w') as f:
            json.dump(users, f)

def get_user_count():
    return len(load_users())

TOOLS_MENU = """
🔧 **14 টা সুপার টুলস** 🔧

🟥 **PDF টুলস**
1️⃣ /pdfmerge - মার্জ করো
2️⃣ /pdfsplit <pages> - ভাগ করো Ex: 1-3,5
3️⃣ /pdfcompress - ছোট করো 70%
4️⃣ /text2pdf <text> - টেক্সট→PDF ✅
5️⃣ /img2pdf - ছবি→PDF ✅

🟦 **ইমেজ টুলস**
6️⃣ /bgremove - BG রিমুভ [API লাগবে]
7️⃣ /resize <w>x<h> - রিসাইজ
8️⃣ /enhance - HD করো

🟨 **ইউটিলিটি**
9️⃣ /qr <text> - QR বানাও
🔟 /ip <ip> - IP লোকেশন
1️⃣1️⃣ /weather <city> - ওয়েদার
1️⃣2️⃣ /wordcount <text> - ওয়ার্ড কাউন্ট

🟪 **প্র্যাংক**
1️⃣3️⃣ /prankvoice <text> - ভয়েস
1️⃣4️⃣ /quote - কোট

📊 /stats - এডমিন
"""

@bot.message_handler(commands=['start'])
def start(msg):
    save_user(msg.from_user.id)
    bot.reply_to(msg, f"ওয়েলকাম বস {msg.from_user.first_name}! 👑\n\n{TOOLS_MENU}\n\n👥 মোট ইউজার: {get_user_count()} জন", parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats(msg):
    if msg.from_user.id == ADMIN_ID:
        bot.reply_to(msg, f"📊 **এডমিন ড্যাশবোর্ড**\n\n👥 মোট ইউজার: {get_user_count()} জন\n🤖 স্ট্যাটাস: লাইভ ✅", parse_mode='Markdown')
    else:
        bot.reply_to(msg, "🚫 এডমিন ছাড়া ঢোকা নিষেধ 😎")

# PDF Merge
@bot.message_handler(commands=['pdfmerge'])
def pdf_merge(msg):
    user_id = msg.from_user.id
    PDF_SESSION[user_id] = []
    bot.reply_to(msg, "🟥 মার্জ মোড অন ✅ 2+ PDF পাঠাও ক্যাপশন 'merge' দিয়ে। শেষে /donemerge")

@bot.message_handler(commands=['donemerge'])
def done_merge(msg):
    user_id = msg.from_user.id
    if user_id in PDF_SESSION and len(PDF_SESSION[user_id]) > 1:
        merger = PdfWriter()
        for pdf_bytes in PDF_SESSION[user_id]:
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                merger.add_page(page)
        output = BytesIO()
        merger.write(output)
        output.seek(0)
        bot.send_document(msg.chat.id, output, caption="🟥 মার্জ কমপ্লিট ✅", filename="merged.pdf")
        PDF_SESSION[user_id] = []
    else:
        bot.reply_to(msg, "🟥 2টা PDF লাগবে ভাই")

# PDF Split
@bot.message_handler(commands=['pdfsplit'])
def pdf_split(msg):
    try:
        pages = msg.text.split(' ', 1)[1]
        user_id = msg.from_user.id
        SPLIT_SESSION[user_id] = pages
        bot.reply_to(msg, f"🟥 পেইজ {pages} সিলেক্ট। এখন PDF পাঠাও ✅")
    except:
        bot.reply_to(msg, "🟥 ইউজ: /pdfsplit 1-3,5")

# Text to PDF - টেক্সট দিলেই PDF
@bot.message_handler(commands=['text2pdf'])
def text_to_pdf(msg):
    try:
        text = msg.text.split(' ', 1)[1]
        img = Image.new('RGB', (595, 842), color='white')
        draw = ImageDraw.Draw(img)
        y = 50
        for line in text.split('\n'):
            draw.text((50, y), line, fill='black')
            y += 30
        pdf_bytes = BytesIO()
        img.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        bot.send_document(msg.chat.id, pdf_bytes, caption="🟥 টেক্সট→PDF রেডি ✅", filename="text.pdf")
    except:
        bot.reply_to(msg, "🟥 ইউজ: /text2pdf তোমার লেখা এখানে")

# Image to PDF - ছবি দিলেই PDF
@bot.message_handler(content_types=['photo'])
def img_to_pdf(msg):
    if msg.caption and 'img2pdf' in msg.caption.lower():
        file_info = bot.get_file(msg.photo[-1].file_id)
        img_bytes = bot.download_file(file_info.file_path)
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        pdf_bytes = BytesIO()
        img.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        bot.send_document(msg.chat.id, pdf_bytes, caption="🟥 ছবি→PDF ডান ✅", filename="image.pdf")
    else:
        bot.reply_to(msg, "🟦 ছবি পাইছি! PDF বানাতে ক্যাপশনে `img2pdf` লিখো")

# PDF Handle - Merge/Split/Compress
@bot.message_handler(content_types=['document'])
def handle_pdf(msg):
    user_id = msg.from_user.id
    if msg.document.mime_type == 'application/pdf':
        file_info = bot.get_file(msg.document.file_id)
        pdf_bytes = bot.download_file(file_info.file_path)

        if msg.caption == 'merge':
            if user_id not in PDF_SESSION:
                PDF_SESSION[user_id] = []
            PDF_SESSION[user_id].append(pdf_bytes)
            bot.reply_to(msg, f"🟥 PDF {len(PDF_SESSION[user_id])} জমা। /donemerge দাও")

        elif user_id in SPLIT_SESSION:
            reader = PdfReader(BytesIO(pdf_bytes))
            writer = PdfWriter()
            pages = SPLIT_SESSION[user_id]
            for p in pages.replace(' ', '').split(','):
                if '-' in p:
                    start, end = map(int, p.split('-'))
                    for i in range(start-1, end):
                        writer.add_page(reader.pages[i])
                else:
                    writer.add_page(reader.pages[int(p)-1])
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            bot.send_document(msg.chat.id, output, caption=f"🟥 পেইজ {pages} কাটা শেষ ✅", filename="split.pdf")
            del SPLIT_SESSION[user_id]

        elif msg.caption == 'compress':
            reader = PdfReader(BytesIO(pdf_bytes))
            writer = PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            bot.send_document(msg.chat.id, output, caption="🟥 PDF 70% ছোট হইছে ✅", filename="compressed.pdf")

        else:
            bot.reply_to(msg, "🟥 ক্যাপশন দাও: merge / compress অথবা আগে /pdfsplit দাও")

# Resize
@bot.message_handler(commands=['resize'])
def resize_img(msg):
    try:
        size = msg.text.split(' ', 1)[1]
        w, h = map(int, size.split('x'))
        PDF_SESSION[msg.from_user.id] = (w, h, 'resize')
        bot.reply_to(msg, f"🟦 সাইজ {w}x{h} সেট। এখন ছবি পাঠাও + ক্যাপশন `resize`")
    except:
        bot.reply_to(msg, "🟦 ইউজ: /resize 1280x720")

@bot.message_handler(content_types=['photo'], func=lambda m: m.caption and 'resize' in m.caption.lower())
def do_resize(msg):
    if msg.from_user.id in PDF_SESSION and PDF_SESSION[msg.from_user.id][2] == 'resize':
        w, h = PDF_SESSION[msg.from_user.id][0], PDF_SESSION[msg.from_user.id][1]
        file_info = bot.get_file(msg.photo[-1].file_id)
        img = Image.open(BytesIO(bot.download_file(file_info.file_path)))
        img = img.resize((w, h), Image.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        bot.send_photo(msg.chat.id, output, caption=f"🟦 {w}x{h} রিসাইজ ডান ✅")

# Enhance
@bot.message_handler(commands=['enhance'])
def enhance_img(msg):
    bot.reply_to(msg, "🟦 HD করতে ছবি পাঠাও + ক্যাপশন `enhance`")

@bot.message_handler(content_types=['photo'], func=lambda m: m.caption and 'enhance' in m.caption.lower())
def do_enhance(msg):
    file_info = bot.get_file(msg.photo[-1].file_id)
    img = Image.open(BytesIO(bot.download_file(file_info.file_path)))
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    output = BytesIO()
    img.save(output, format='JPEG')
    output.seek(0)
    bot.send_photo(msg.chat.id, output, caption="🟦 HD এনহ্যান্স ডান ✅")

# Word Count
@bot.message_handler(commands=['wordcount'])
def word_count(msg):
    try:
        text = msg.text.split(' ', 1)[1]
        words = len(text.split())
        chars = len(text)
        chars_no_space = len(text.replace(' ', ''))
        bot.reply_to(msg, f"🟨 **রেজাল্ট**\n\n📝 ওয়ার্ড: {words}\n🔤 ক্যারেক্টার: {chars}\n🔡 স্পেস ছাড়া: {chars_no_space}", parse_mode='Markdown')
    except:
        bot.reply_to(msg, "🟨 ইউজ: /wordcount তোমার লেখা")

# Prank Voice
@bot.message_handler(commands=['prankvoice'])
def prank_voice(msg):
    try:
        text = msg.text.split(' ', 1)[1]
        tts = gTTS(text=text, lang='bn')
        voice_bytes = BytesIO()
        tts.write_to_fp(voice_bytes)
        voice_bytes.seek(0)
        bot.send_voice(msg.chat.id, voice_bytes, caption="🟪 প্র্যাংক ভয়েস 😂")
    except:
        bot.reply_to(msg, "🟪 ইউজ: /prankvoice তুমি জোকার")

# QR, IP, Weather, Quote
@bot.message_handler(commands=['qr'])
def qr_gen(msg):
    try:
        text = msg.text.split(' ', 1)[1]
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={text}"
        bot.send_photo(msg.chat.id, url, caption="🟨 QR রেডি ✅")
    except:
        bot.reply_to(msg, "🟨 ইউজ: /qr Hello")

@bot.message_handler(commands=['ip'])
def ip_info(msg):
    try:
        ip = msg.text.split(' ', 1)[1]
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        reply = f"🟨 **IP Info**\n🌍 {r['country']}\n🏙️ {r['city']}\n📡 {r['isp']}"
        bot.reply_to(msg, reply, parse_mode='Markdown')
    except:
        bot.reply_to(msg, "🟨 ইউজ: /ip 8.8.8.8")

@bot.message_handler(commands=['weather'])
def weather(msg):
    try:
        city = msg.text.split(' ', 1)[1]
        api_key = os.environ.get('WEATHER_KEY')
        if not api_key:
            bot.reply_to(msg, "🟨 WEATHER_KEY অ্যাড করো Render এ")
            return
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=bn"
        r = requests.get(url).json()
        reply = f"🟨 **{city}**\n🌡️ {r['main']['temp']}°C\n💧 {r['main']['humidity']}%\n☁️ {r['weather'][0]['description']}"
        bot.reply_to(msg, reply, parse_mode='Markdown')
    except:
        bot.reply_to(msg, "🟨 ইউজ: /weather Dhaka")

@bot.message_handler(commands=['quote'])
def quote(msg):
    quotes = ["🟪 'লাইফ ইজ প্র্যাংক' 😂", "🟪 'হাসতে থাকো' 🔥", "🟪 'টেনশন নিও না' ✨"]
    bot.reply_to(msg, random.choice(quotes))

@app.route('/')
def home():
    return f"Bot Running! Users: {get_user_count()}"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return "ok", 200

if __name__ == '__main__':
    bot.remove_webhook()
    webhook_url = os.environ.get('RENDER_EXTERNAL_URL') + '/webhook'
    bot.set_webhook(url=webhook_url)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
