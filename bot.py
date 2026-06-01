import os
import random
import datetime
import asyncio
from flask import Flask, request
import telebot
from telebot import types
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import edge_tts

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
RENDER_URL = os.environ.get('RENDER_URL')

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}

# ফন্ট ফিক্সড ভার্সন - বাংলা + ইংলিশ দুইটাই সাপোর্ট করে
# ইংলিশ ফন্ট রেজিস্টার
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
def download_font():
    font_path = "/tmp/NotoSansBengali.ttf"
    if os.path.exists(font_path) and os.path.getsize(font_path) < 100000:
        os.remove(font_path)
    if not os.path.exists(font_path):
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf"
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
    return font_path

FONT_PATH = download_font()

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
    return "Shanu's Magic Bot v6 - 17 Tools 🔥"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(btn) for btn in tools.values()])
    bot.send_message(message.chat.id,
                     "🔥 **Shanu's Magic Bot v6**\n\n"
                     "17টা ভাইরাল টুল রেডি। সব ফ্রি + ফাস্ট\n"
                     "`/cancel` দিয়ে বাতিল করো",
                     reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    cancel_prev(message.chat.id)

def cancel_prev(chat_id):
    if user_state.get(chat_id):
        user_state[chat_id] = None
        bot.send_message(chat_id, "ক্যান্সেল হলো ✅")

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
    user_state[message.chat.id] = None

# 2. # 2. Text → PDF - English + Bangla সাপোর্টেড
@bot.message_handler(func=lambda m: m.text == "📝 টেক্সট → PDF")
def txt_pdf_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'txt_pdf'
    bot.send_message(message.chat.id, "📝 PDF এ যেটা লিখতে চাও সেটা পাঠাও\nবাংলা + ইংলিশ দুইটাই লিখতে পারবা")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'txt_pdf')
def txt_pdf_process(message):
    try:
        # DejaVuSans.ttf ইউজ করো - বাংলা + ইংলিশ দুইটাই সাপোর্ট করে
        pdfmetrics.registerFont(TTFont('Bengali', 'DejaVuSans.ttf'))
        c = canvas.Canvas("/tmp/text.pdf", pagesize=A4)
        width, height = A4
        c.setFont('Bengali', 14)
        
        y = height - 50
        for line in message.text.split('\n'):
            # UTF-8 এনকোডিং নিশ্চিত করো
            c.drawString(50, y, line.encode('utf-8').decode('utf-8'))
            y -= 25
            if y < 50:
                c.showPage()
                c.setFont('Bengali', 14)  # নতুন পেজে আবার ফন্ট সেট করো
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

# 16. BD Female Voice TTS
@bot.message_handler(func=lambda m: m.text == "🎤 BD Female Voice")
def female_voice_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'female_tts'
    bot.send_message(message.chat.id, "🎤 টেক্সট লিখো, বাংলাদেশী ফিমেল ভয়েসে বলবো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'female_tts')
def female_voice_process(message):
    try:
        async def tts():
            communicate = edge_tts.Communicate(message.text, "bn-BD-NadiaNeural")
            await communicate.save("/tmp/female.mp3")
        asyncio.run(tts())
        with open("/tmp/female.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption="✅ BD Female Voice রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

# 17. BD Male Voice TTS
@bot.message_handler(func=lambda m: m.text == "🎤 BD Male Voice")
def male_voice_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'male_tts'
    bot.send_message(message.chat.id, "🎤 টেক্সট লিখো, বাংলাদেশী মেল ভয়েসে বলবো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'male_tts')
def male_voice_process(message):
    try:
        async def tts():
            communicate = edge_tts.Communicate(message.text, "bn-BD-PradeepNeural")
            await communicate.save("/tmp/male.mp3")
        asyncio.run(tts())
        with open("/tmp/male.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption="✅ BD Male Voice রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")

@bot.message_handler(func=lambda m: True)
def default_handler(message):
    if user_state.get(message.chat.id):
        bot.send_message(message.chat.id, "প্রথমে কাজটা শেষ করো 👆 অথবা `/cancel` লিখো")
    else:
        bot.send_message(message.chat.id, "মেনু থেকে অপশন সিলেক্ট করো 👇")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/webhook")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
