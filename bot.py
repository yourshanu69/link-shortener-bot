import os
import telebot
import json
import random
import traceback
import uuid
from datetime import datetime
from flask import Flask, request
from PIL import Image, ImageEnhance, ImageDraw
from io import BytesIO
import requests
from gtts import gTTS
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

USER_FILE = 'users.json'
TEMP_DIR = '/tmp/bot_images'
os.makedirs(TEMP_DIR, exist_ok=True)

SESSION = {}

def get_session(user_id):
    if user_id not in SESSION:
        SESSION[user_id] = {'mode': None, 'image_paths': [], 'files': [], 'pages': '', 'size': (1280, 720)}
        print(f"DEBUG: New session created for {user_id}", flush=True)
    return SESSION[user_id]

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user(user_id, first_name, username):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            'name': first_name,
            'username': username if username else 'None',
            'join_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        with open(USER_FILE, 'w') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

def get_user_count():
    return len(load_users())

def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton('🟥 PDF মার্জ'),
        KeyboardButton('🟥 PDF ভাগ'),
        KeyboardButton('🟥 PDF ছোট করো'),
        KeyboardButton('🟥 টেক্সট→PDF'),
        KeyboardButton('🟥 ছবি→PDF'),
        KeyboardButton('🟦 রিসাইজ ছবি'),
        KeyboardButton('🟦 HD করো'),
        KeyboardButton('🟨 QR বানাও'),
        KeyboardButton('🟨 IP চেক'),
        KeyboardButton('🟨 ওয়েদার'),
        KeyboardButton('🟨 ওয়ার্ড কাউন্ট'),
        KeyboardButton('🟪 প্র্যাংক ভয়েস'),
        KeyboardButton('🟪 মোটিভেশন'),
        KeyboardButton('🔄 /cancel'),
        KeyboardButton('📊 এডমিন')
    )
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    save_user(msg.from_user.id, msg.from_user.first_name, msg.from_user.username)
    get_session(msg.from_user.id)
    if msg.from_user.id == ADMIN_ID:
        bot.send_message(msg.chat.id, f"ওয়েলকাম বস {msg.from_user.first_name}! 👑\nনিচের বাটন চাপো 👇\n👥 ইউজার: {get_user_count()} জন", reply_markup=main_keyboard())
    else:
        bot.send_message(msg.chat.id, f"ওয়েলকাম বস {msg.from_user.first_name}! 👑\nনিচের বাটন চাপো 👇", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == '🔄 /cancel')
def cancel_mode(msg):
    user_id = msg.from_user.id
    session = get_session(user_id)
    for filepath in session.get('image_paths', []):
        if os.path.exists(filepath):
            os.remove(filepath)
    SESSION[user_id] = {'mode': None, 'image_paths': [], 'files': [], 'pages': '', 'size': (1280, 720)}
    bot.send_message(msg.chat.id, "❌ সব রিসেট ডান। আবার বাটন চাপো", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == '🟥 ছবি→PDF')
def btn_img2pdf(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'img2pdf_batch'
    session['image_paths'] = []
    bot.reply_to(msg, "🟥 ব্যাচ মোড অন ✅\nযত খুশি ছবি পাঠাও। শেষে /donepdf দাও")

@bot.message_handler(func=lambda m: m.text == '🟥 PDF মার্জ')
def btn_pdfmerge(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'merge'
    session['files'] = []
    bot.reply_to(msg, "🟥 মার্জ মোড অন ✅\n2+ PDF পাঠাও। ক্যাপশনে `merge` লিখবা। শেষে /donemerge দাও")

@bot.message_handler(func=lambda m: m.text == '🟥 PDF ভাগ')
def btn_pdfsplit(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'split_wait_pages'
    bot.reply_to(msg, "🟥 কত পেইজ কাটবা লিখো। Ex: 1-3,5\nলেখার পর PDF পাঠাও")

@bot.message_handler(func=lambda m: m.text == '🟥 PDF ছোট করো')
def btn_pdfcompress(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'compress'
    bot.reply_to(msg, "🟥 PDF পাঠাও। ক্যাপশনে `compress` লিখে দাও ✅")

@bot.message_handler(func=lambda m: m.text == '🟥 টেক্সট→PDF')
def btn_text2pdf(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'text2pdf'
    bot.reply_to(msg, "🟥 লেখা পাঠাও। আমি সাথে PDF বানায় দিবো ✅")

@bot.message_handler(func=lambda m: m.text == '🟦 রিসাইজ ছবি')
def btn_resize(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'resize_wait_size'
    bot.reply_to(msg, "🟦 সাইজ লিখো: 1280x720\nতারপর ছবি পাঠাও ✅")

@bot.message_handler(func=lambda m: m.text == '🟦 HD করো')
def btn_enhance(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'enhance'
    bot.reply_to(msg, "🟦 ছবি পাঠাও। ক্যাপশন লাগবে না ✅")

@bot.message_handler(func=lambda m: m.text == '🟨 QR বানাও')
def btn_qr(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'qr'
    bot.reply_to(msg, "🟨 কি লিখে QR বানাবা? লিখো ✅")

@bot.message_handler(func=lambda m: m.text == '🟨 IP চেক')
def btn_ip(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'ip'
    bot.reply_to(msg, "🟨 IP লিখো: 8.8.8.8")

@bot.message_handler(func=lambda m: m.text == '🟨 ওয়েদার')
def btn_weather(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'weather'
    bot.reply_to(msg, "🟨 শহরের নাম লিখো: Dhaka")

@bot.message_handler(func=lambda m: m.text == '🟨 ওয়ার্ড কাউন্ট')
def btn_wordcount(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'wordcount'
    bot.reply_to(msg, "🟨 লেখা পাঠাও। ওয়ার্ড গুনে দিবো ✅")

@bot.message_handler(func=lambda m: m.text == '🟪 প্র্যাংক ভয়েস')
def btn_prank(msg):
    session = get_session(msg.from_user.id)
    session['mode'] = 'prankvoice'
    bot.reply_to(msg, "🟪 কি বলবা? লিখো ✅")

@bot.message_handler(func=lambda m: m.text == '🟪 মোটিভেশন')
def btn_quote(msg):
    quotes = ["🟪 'লাইফ ইজ প্র্যাংক' 😂", "🟪 'হাসতে থাকো' 🔥", "🟪 'টেনশন নিও না' ✨", "🟪 'ঘুমাও বস' 😴"]
    bot.reply_to(msg, random.choice(quotes))

@bot.message_handler(func=lambda m: m.text == '📊 এডমিন')
def btn_stats(msg):
    if msg.from_user.id == ADMIN_ID:
        users = load_users()
        total = len(users)
        text = f"📊 **এডমিন ড্যাশবোর্ড**\n\n👥 মোট ইউজার: {total} জন\n🤖 স্ট্যাটাস: লাইভ ✅\n\n**ইউজার লিস্ট:**\n\n"
        count = 1
        for uid, data in users.items():
            text += f"{count}. `{uid}`\n নাম: {data['name']}\n ইউজার: @{data['username']}\n জয়েন: {data['join_date']}\n\n"
            count += 1
            if count > 30:
                text += f"...আর {total-30} জন আছে"
                break
        bot.reply_to(msg, text, parse_mode='Markdown')
    else:
        bot.reply_to(msg, "🚫 এডমিন ছাড়া ঢোকা নিষেধ 😎")

@bot.message_handler(func=lambda m: m.from_user.id in SESSION)
def handle_text(msg):
    user_id = msg.from_user.id
    session = get_session(user_id)
    mode = session.get('mode')
    text = msg.text

    if mode == 'split_wait_pages':
        session['pages'] = text
        session['mode'] = 'split_wait_pdf'
        bot.reply_to(msg, f"🟥 পেইজ {text} সেট। এখন PDF পাঠাও ✅")
        return

    if mode == 'text2pdf':
        try:
            img = Image.new('RGB', (595, 842), 'white')
            draw = ImageDraw.Draw(img)
            y = 50
            for line in text.split('\n')[:35]:
                draw.text((50, y), line, fill='black')
                y += 22
            pdf_bytes = BytesIO()
            img.save(pdf_bytes, format='PDF', save_all=True)
            pdf_bytes.seek(0)
            pdf_bytes.name = "text.pdf"
            bot.send_document(msg.chat.id, pdf_bytes, caption="🟥 টেক্সট→PDF ডান ✅")
        except Exception as e:
            bot.reply_to(msg, f"🟥 PDF বানাতে সমস্যা: {e}")
        session['mode'] = None
        return

    if mode == 'qr':
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={text}"
        bot.send_photo(msg.chat.id, url, caption="🟨 QR রেডি ✅")
        session['mode'] = None
        return

    if mode == 'ip':
        try:
            r = requests.get(f"http://ip-api.com/json/{text}").json()
            bot.reply_to(msg, f"🟨 **IP Info**\n🌍 {r['country']}\n🏙️ {r['city']}\n📡 {r['isp']}", parse_mode='Markdown')
        except:
            bot.reply_to(msg, "🟨 ভুল IP")
        session['mode'] = None
        return

    if mode == 'weather':
        api_key = os.environ.get('WEATHER_KEY')
        if not api_key:
            bot.reply_to(msg, "🟨 WEATHER_KEY অ্যাড করো Railway এ")
            return
        try:
            r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={text}&appid={api_key}&units=metric&lang=bn").json()
            bot.reply_to(msg, f"🟨 **{text}**\n🌡️ {r['main']['temp']}°C\n💧 {r['main']['humidity']}%\n☁️ {r['weather'][0]['description']}", parse_mode='Markdown')
        except:
            bot.reply_to(msg, "🟨 শহর পাওয়া যায় নাই")
        session['mode'] = None
        return

    if mode == 'wordcount':
        words = len(text.split())
        chars = len(text)
        bot.reply_to(msg, f"🟨 **রেজাল্ট**\n📝 ওয়ার্ড: {words}\n🔤 ক্যারেক্টার: {chars}", parse_mode='Markdown')
        session['mode'] = None
        return

    if mode == 'prankvoice':
        tts = gTTS(text=text, lang='bn')
        voice_bytes = BytesIO()
        tts.write_to_fp(voice_bytes)
        voice_bytes.seek(0)
        bot.send_voice(msg.chat.id, voice_bytes, caption="🟪 প্র্যাংক ভয়েস 😂")
        session['mode'] = None
        return

    if mode == 'resize_wait_size':
        try:
            w, h = map(int, text.split('x'))
            session['size'] = (w, h)
            session['mode'] = 'resize_wait_img'
            bot.reply_to(msg, f"🟦 {w}x{h} সেট। এখন ছবি পাঠাও ✅")
        except:
            bot.reply_to(msg, "🟦 ভুল ফরম্যাট। Ex: 1280x720")

@bot.message_handler(content_types=['document'])
def handle_pdf(msg):
    user_id = msg.from_user.id
    session = get_session(user_id)
    if msg.document.mime_type!= 'application/pdf':
        return

    file_info = bot.get_file(msg.document.file_id)
    pdf_bytes = bot.download_file(file_info.file_path)
    mode = session.get('mode')

    if mode == 'merge' and msg.caption == 'merge':
        session['files'].append(pdf_bytes)
        bot.reply_to(msg, f"🟥 PDF {len(session['files'])} জমা। /donemerge দাও")

    elif mode == 'split_wait_pdf':
        try:
            pages = session['pages']
            reader = PdfReader(BytesIO(pdf_bytes))
            writer = PdfWriter()
            for p in pages.replace(' ', '').split(','):
                if '-' in p:
                    s, e = map(int, p.split('-'))
                    for i in range(s-1, e):
                        writer.add_page(reader.pages[i])
                else:
                    writer.add_page(reader.pages[int(p)-1])
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            output.name = "split.pdf"
            bot.send_document(msg.chat.id, output, caption=f"🟥 পেইজ {pages} কাটা শেষ ✅")
        except Exception as e:
            bot.reply_to(msg, f"🟥 কাটতে সমস্যা: {e}")
        session['mode'] = None

    elif mode == 'compress' and msg.caption == 'compress':
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            writer = PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            output.name = "compressed.pdf"
            bot.send_document(msg.chat.id, output, caption="🟥 PDF 70% ছোট ✅")
        except Exception as e:
            bot.reply_to(msg, f"🟥 কম্প্রেস সমস্যা: {e}")
        session['mode'] = None

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    user_id = msg.from_user.id
    session = get_session(user_id)
    mode = session.get('mode')

    if mode == 'img2pdf_batch':
        try:
            file_info = bot.get_file(msg.photo[-1].file_id)
            img_data = bot.download_file(file_info.file_path)
            filename = f"{user_id}_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(TEMP_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            session['image_paths'].append(filepath)
            bot.reply_to(msg, f"🟥 ছবি {len(session['image_paths'])} জমা ✅\nআর পাঠাও। শেষে /donepdf দাও")
        except Exception as e:
            bot.reply_to(msg, f"🟦 ছবি সেভ করতে সমস্যা: {e}")

    elif mode == 'resize_wait_img':
        try:
            file_info = bot.get_file(msg.photo[-1].file_id)
            img_data = bot.download_file(file_info.file_path)
            img = Image.open(BytesIO(img_data))
            w, h = session['size']
            img_resized = img.resize((w, h), Image.LANCZOS)
            output = BytesIO()
            img_resized.save(output, format='JPEG', quality=95)
            output.seek(0)
            bot.send_photo(msg.chat.id, output, caption=f"🟦 {w}x{h} রিসাইজ ডান ✅")
            session['mode'] = None
        except Exception as e:
            bot.reply_to(msg, f"🟦 রিসাইজ সমস্যা: {e}")

    elif mode == 'enhance':
        try:
            file_info = bot.get_file(msg.photo[-1].file_id)
            img_data = bot.download_file(file_info.file_path)
            img = Image.open(BytesIO(img_data))
            enhancer = ImageEnhance.Sharpness(img)
            img_enhanced = enhancer.enhance(2.0)
            output = BytesIO()
            img_enhanced.save(output, format='JPEG', quality=95)
            output.seek(0)
            bot.send_photo(msg.chat.id, output, caption="🟦 HD এনহ্যান্স ডান ✅")
            session['mode'] = None
        except Exception as e:
            bot.reply_to(msg, f"🟦 HD সমস্যা: {e}")

@bot.message_handler(commands=['donemerge'])
def done_merge(msg):
    user_id = msg.from_user.id
    session = get_session(user_id)
    if len(session.get('files', [])) < 2:
        bot.reply_to(msg, "🟥 কমপক্ষে 2টা PDF লাগবে")
        return
    try:
        merger = PdfWriter()
        for pdf_bytes in session['files']:
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                merger.add_page(page)
        output = BytesIO()
        merger.write(output)
        output.seek(0)
        output.name = "merged.pdf"
        bot.send_document(msg.chat.id, output, caption=f"🟥 {len(session['files'])}টা PDF মার্জ কমপ্লিট ✅")
        session['files'] = []
        session['mode'] = None
    except Exception as e:
        bot.reply_to(msg, f"🟥 মার্জ করতে সমস্যা: {e}")
        session['mode'] = None

@bot.message_handler(commands=['donepdf'])
def done_pdf(msg):
    user_id = msg.from_user.id
    session = get_session(user_id)

    if len(session.get('image_paths', [])) < 1:
        bot.reply_to(msg, "🟥 ছবি 0টা জমা আছে। আগে '🟥 ছবি→PDF' চেপে ছবি পাঠাও")
        return

    bot.reply_to(msg, f"🟥 {len(session['image_paths'])}টা ছবি প্রসেস করতেছি... 30 সেকেন্ড ⏳")

    try:
        images = []
        for filepath in session['image_paths']:
            img = Image.open(filepath).convert('RGB')
            max_size = 800
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.LANCZOS)
            images.append(img)

        pdf_bytes = BytesIO()
        if len(images) > 1:
            images[0].save(pdf_bytes, format='PDF', save_all=True, append_images=images[1:], resolution=72.0, optimize=True)
        else:
            images[0].save(pdf_bytes, format='PDF', resolution=72.0, optimize=True)

        pdf_bytes.seek(0)
        pdf_bytes.name = "batch_images.pdf"
        size_mb = round(len(pdf_bytes.getvalue())/1024/1024, 2)
        bot.send_document(msg.chat.id, pdf_bytes, caption=f"🟥 {len(images)}টা ছবি→1টা PDF ডান ✅\nসাইজ: {size_mb} MB")

        for filepath in session['image_paths']:
            if os.path.exists(filepath):
                os.remove(filepath)
        session['image_paths'] = []

    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}", flush=True)
        bot.reply_to(msg, f"🟥 এরর: {str(e)}")
        for filepath in session.get('image_paths', []):
            if os.path.exists(filepath):
                os.remove(filepath)
        session['image_paths'] = []

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

    # Railway এর জন্য ফিক্স
    domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    if domain:
        webhook_url = f"https://{domain}/webhook"
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set: {webhook_url}", flush=True)
    else:
        print("RAILWAY_PUBLIC_DOMAIN নাই", flush=True)

    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
