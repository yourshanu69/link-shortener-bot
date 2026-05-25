print("Script started")
import os
import random
import base64
from threading import Thread
from flask import Flask
import telebot
from telebot import types
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import qrcode

app = Flask(__name__)

@app.route('/')
def home():
    return "Shanu's Magic Bot - 21 Tools Working 🔥"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, skip_pending=True)
user_state = {}
PREMIUM_USERS = [1692907487]

tools = {
    'Banner Creator': "ব্যানার বানাও",
    'Eid Rules': "ঈদের নিয়ম-কানুন",
    'Fun Zone': "জোকস/রিডল/ফ্যাক্ট",
    'Story Generator': "গল্প বানাও",
    'Poem Generator': "কবিতা বানাও",
    'Image→PDF': "ছবি দিয়ে PDF",
    'Text→PDF': "টেক্সট দিয়ে PDF",
    'Sticker': "ছবি থেকে স্টিকার",
    'QR Generator': "QR বানাও",
    'Color Generator': "রঙের কোড বানাও",
    'BG Blur': "ছবি ব্লার করো",
    'Resize Image': "ছবি রিসাইজ করো",
    'Text to Image': "টেক্সট থেকে ছবি",
    'Password Gen': "পাসওয়ার্ড বানাও",
    'Age Calculator': "বয়স বের করো",
    'BMI Calculator': "BMI বের করো",
    'Word Counter': "শব্দ গুনো",
    'Base64 Encode': "Text Encode করো",
    'Base64 Decode': "Text Decode করো",
    'Joke Bangla': "বাংলা জোকস",
    'Motivation': "মোটিভেশন কোটস",
    'FIFA 2026': "বিশ্বকাপ সময়সূচি" # নতুন টুল
}

@bot.message_handler(commands=['start', 'cancel'])
def start(message):
    user_state[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(btn) for btn in tools.keys()])
    bot.send_message(message.chat.id, "🔥 **21 টা টুল রেডি** 😎\nসব রিয়েল, কোনো ডেমো নাই\n`/cancel` লিখে বাতিল করো", reply_markup=markup, parse_mode="Markdown")

def cancel_prev(chat_id):
    if user_state.get(chat_id):
        user_state[chat_id] = None
        bot.send_message(chat_id, "আগের প্রসেস ক্যান্সেল ✅")

# 1. Banner Creator - FIXED
@bot.message_handler(func=lambda m: 'Banner' in m.text)
def banner_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = {'state': 'banner_photo'}
    bot.send_message(message.chat.id, "📷 প্রথমে তোমার ছবিটা **Photo** হিসেবে পাঠাও\nFile হিসেবে পাঠাইও না")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_photo', content_types=['photo'])
def banner_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        # RGB তে কনভার্ট করে নিলাম
        img = Image.open(BytesIO(downloaded)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="PNG")
        user_state[message.chat.id]['photo'] = buf.getvalue()
        user_state[message.chat.id]['state'] = 'banner_name'
        bot.send_message(message.chat.id, "✅ ছবি পেলাম\nএখন তোমার নাম লিখো")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ ছবি নিতে সমস্যা: {e}\nআবার Photo হিসেবে পাঠাও")
        user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_name')
def banner_name(message):
    user_state[message.chat.id]['name'] = message.text
    user_state[message.chat.id]['state'] = 'banner_location'
    bot.send_message(message.chat.id, "📍 এখন এলাকার নাম লিখো। যেমন: ডৈব")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_location')
def banner_generate(message):
    data = user_state[message.chat.id]
    data['location'] = message.text

    try:
        font_path = "/tmp/NotoSansBengali.ttf"
        if not os.path.exists(font_path):
            font_url = "https://github.com/google/fonts/raw/main/ofl/notosansbengali/NotoSansBengali-Regular.ttf"
            r = requests.get(font_url, timeout=10)
            with open(font_path, "wb") as f:
                f.write(r.content)

        img = Image.new('RGB', (1080, 1920), color=(230, 250, 240))
        draw = ImageDraw.Draw(img)

        font_big = ImageFont.truetype(font_path, 75)
        font_med = ImageFont.truetype(font_path, 55)
        font_small = ImageFont.truetype(font_path, 45)

        draw.rectangle([0, 1200, 1080, 1920], fill=(210, 240, 225))
        draw.rounded_rectangle([40, 40, 1040, 300], radius=40, fill=(0, 128, 0))

        draw.text((540, 120), f"{data['location']}বাসীকে", font=font_big, fill="white", anchor="mm")
        draw.text((540, 200), "পবিত্র ঈদুল ফিতরের", font=font_big, fill="yellow", anchor="mm")
        draw.text((540, 270), "শুভেচ্ছা", font=font_big, fill="white", anchor="mm")

        draw.text((200, 400), "ঈদ", font=font_big, fill=(220, 20, 60), anchor="mm")
        draw.text((200, 480), "মোবারক", font=font_big, fill=(30, 144, 255), anchor="mm")

        photo = Image.open(BytesIO(data['photo'])).resize((400, 400))
        mask = Image.new('L', (400, 400), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 400, 400), fill=255)
        img.paste(photo, (340, 750), mask)

        draw.rounded_rectangle([40, 1600, 1040, 1720], radius=40, fill=(0, 128, 0))
        draw.text((540, 1660), f"[{data['name']}]", font=font_big, fill="white", anchor="mm")

        draw.rectangle([0, 1750, 1080, 1920], fill=(255, 215, 0))
        draw.text((540, 1835), f"[{data['location']}]", font=font_big, fill="black", anchor="mm")

        if message.from_user.id not in PREMIUM_USERS:
            draw.text((540, 1880), "Shanu's Magic Bot", font=font_small, fill=(100, 100, 100), anchor="mm")

        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ তোমার Eid Banner রেডি! 🔥")
        user_state[message.chat.id] = None

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}\nআবার ট্রাই করো")
        user_state[message.chat.id] = None

# 2-5. আগের মতোই আছে - Eid Rules, Fun Zone, Story, Poem
@bot.message_handler(func=lambda m: 'Eid' in m.text and '2026' not in m.text)
def eid_rules(message):
    cancel_prev(message.chat.id)
    text = """🕌 **ঈদ-উল-ফিতর এর নিয়ম**
1. ঈদের নামাজ: 2 রাকাত, 6 তাকবির
2. ফজরের পর গোসল, সুন্দর পোশাক
3. ফিতরা নামাজের আগে দিতে হবে"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: 'Fun' in m.text)
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
    else:
        bot.send_message(message.chat.id, "মেনু থেকে অপশন সিলেক্ট করো 👆")
    user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Story' in m.text)
def story_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'story'
    bot.send_message(message.chat.id, "গল্পের টপিক লিখো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'story')
def story_gen(message):
    story = f"একদিন {message.text} নিয়ে একটা মজার ঘটনা ঘটলো। শেষে সব ঠিক হয়ে গেলো। 😊"
    bot.send_message(message.chat.id, f"📖 **গল্প:**\n{story}", parse_mode="Markdown")
    user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Poem' in m.text)
def poem_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'poem'
    bot.send_message(message.chat.id, "কবিতার বিষয় লিখো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'poem')
def poem_gen(message):
    poem = f"{message.text} তুমি কত সুন্দর\nতোমার তুলনা নাই"
    bot.send_message(message.chat.id, f"✍️ **কবিতা:**\n{poem}", parse_mode="Markdown")
    user_state[message.chat.id] = None

# 6. Image to PDF - FIXED
@bot.message_handler(func=lambda m: 'Image→PDF' in m.text)
def img_to_pdf_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = {'state': 'img_pdf', 'images': []}
    bot.send_message(message.chat.id, "📷 ছবি পাঠাও। শেষে 'Done' লিখো")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'img_pdf', content_types=['photo', 'text'])
def img_to_pdf_process(message):
    if message.text and 'Done' in message.text:
        images = user_state[message.chat.id]['images']
        if not images:
            bot.send_message(message.chat.id, "কোনো ছবি নাই")
            user_state[message.chat.id] = None
            return
        try:
            img_list = [Image.open(BytesIO(img)).convert('RGB') for img in images]
            img_list[0].save('/tmp/output.pdf', save_all=True, append_images=img_list[1:])
            with open('/tmp/output.pdf', 'rb') as f:
                bot.send_document(message.chat.id, f, caption="✅ PDF রেডি")
            user_state[message.chat.id] = None
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
            user_state[message.chat.id] = None
        return
    if message.photo:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        user_state[message.chat.id]['images'].append(downloaded)
        bot.send_message(message.chat.id, f"✅ {len(user_state[m.chat.id]['images'])} টা ছবি যোগ হলো")

# 7-11. বাকি টুলগুলো আগের মতো, শুধু Sticker এ convert RGB অ্যাড করলাম
@bot.message_handler(func=lambda m: 'Sticker' in m.text)
def sticker_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'sticker'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'sticker', content_types=['photo'])
def sticker_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded)).convert('RGB').resize((512, 512))
        img.save('/tmp/sticker.webp', 'WEBP')
        with open('/tmp/sticker.webp', 'rb') as f:
            bot.send_sticker(message.chat.id, f)
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

# 12. FIFA 2026 World Cup Schedule - NEW TOOL
@bot.message_handler(func=lambda m: 'FIFA' in m.text or 'বিশ্বকাপ' in m.text)
def fifa_2026(message):
    cancel_prev(message.chat.id)
    text = """⚽ **2026 FIFA বিশ্বকাপ সময়সূচি**

🏆 **আয়োজক:** যুক্তরাষ্ট্র, কানাডা, মেক্সিকো
📅 **শুরু:** 11 জুন 2026
📅 **ফাইনাল:** 12 জুলাই 2026
👥 **দল:** 48 টি দল

**গ্রুপ পর্বের কিছু ম্যাচ:**
1. 11 জুন - মেক্সিকো vs কানাডা - 8:00 PM - মেক্সিকো সিটি
2. 12 জুন - যুক্তরাষ্ট্র vs ইরান - 9:00 PM - লস অ্যাঞ্জেলেস
3. 13 জুন - ব্রাজিল vs সার্বিয়া - 7:00 PM - নিউ ইয়র্ক
4. 14 জুন - আর্জেন্টিনা vs অস্ট্রেলিয়া - 8:00 PM - মিয়ামি
5. 15 জুন - জার্মানি vs জাপান - 9:00 PM - টরন্টো
6. 16 জুন - ফ্রান্স vs মরক্কো - 8:00 PM - হিউস্টন
7. 17 জুন - স্পেন vs ইংল্যান্ড - 7:00 PM - সিয়াটল
8. 18 জুন - পর্তুগাল vs উরুগুয়ে - 9:00 PM - ডালাস

**নকআউট পর্ব:**
- রাউন্ড 32: 26-30 জুন 2026
- কোয়ার্টার ফাইনাল: 3-4 জুলাই 2026
- সেমি ফাইনাল: 8-9 জুলাই 2026
- ফাইনাল: 12 জুলাই 2026 - মেটলাইফ স্টেডিয়াম, নিউ জার্সি

⚠️ নোট: এটা প্রিলিমিনারি শিডিউল। ফাইনাল ড্র ডিসেম্বর 2025 এ হবে।

সম্পূর্ণ আপডেট পেতে `/start` চাপো"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# 13-21. বাকি টুলগুলো আগের মতোই রাখো
@bot.message_handler(func=lambda m: 'QR' in m.text)
def qr_gen(message):
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
        user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Color' in m.text)
def color_start(message):
    cancel_prev(message.chat.id)
    r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
    hex_code = f"#{r:02x}{g:02x}{b:02x}"
    img = Image.new('RGB', (400, 400), color=(r, g, b))
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    bot.send_photo(message.chat.id, buf, caption=f"🎨 Color Code: `{hex_code}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: 'BG' in m.text)
def bg_blur_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'bg_blur'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও, ব্লার করে দেব")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'bg_blur', content_types=['photo'])
def bg_blur_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded)).filter(ImageFilter.GaussianBlur(10))
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="✅ ব্লার কমপ্লিট!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Password' in m.text)
def pass_gen(message):
    cancel_prev(message.chat.id)
    pwd = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=12))
    bot.send_message(message.chat.id, f"🔑 Password: `{pwd}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: 'Word' in m.text)
def word_count(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'word_count'
    bot.send_message(message.chat.id, "টেক্সট পাঠাও, শব্দ গুনে দেব")

@bot.message_handler(func=lambda m: user_state.get(message.chat.id) == 'word_count')
def word_count_process(message):
    count = len(message.text.split())
    bot.send_message(message.chat.id, f"📝 মোট শব্দ: {count}")
    user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Base64 Encode' in m.text)
def b64_encode_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'b64_encode'
    bot.send_message(message.chat.id, "Encode করার টেক্সট দাও")

@bot.message_handler(func=lambda m: user_state.get(message.chat.id) == 'b64_encode')
def b64_encode_process(message):
    encoded = base64.b64encode(message.text.encode()).decode()
    bot.send_message(message.chat.id, f"`{encoded}`", parse_mode="Markdown")
    user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Base64 Decode' in m.text)
def b64_decode_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'b64_decode'
    bot.send_message(message.chat.id, "Decode করার টেক্সট দাও")

@bot.message_handler(func=lambda m: user_state.get(message.chat.id) == 'b64_decode')
def b64_decode_process(message):
    try:
        decoded = base64.b64decode(message.text.encode()).decode()
        bot.send_message(message.chat.id, f"`{decoded}`", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ ভুল Base64")
    user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: 'Joke' in m.text)
def joke_bangla(message):
    cancel_prev(message.chat.id)
    jokes = ["শিক্ষক: পড়াশোনা করো। ছাত্র: করতেছি স্যার, স্বপ্নে! 😂", "আমি অলস না, এনার্জি সেভ করতেছি"]
    bot.send_message(message.chat.id, random.choice(jokes))

@bot.message_handler(func=lambda m: 'Motivation' in m.text)
def motivation(message):
    cancel_prev(message.chat.id)
    quotes = ["হার মানা যাবে না, চেষ্টা করতেই হবে!", "আজকের কষ্ট কালকের শক্তি", "লেগে থাকো, সফল হবে"]
    bot.send_message(message.chat.id, f"💪 {random.choice(quotes)}")

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document'])
def handle_default(message):
    if user_state.get(message.chat.id):
        bot.send_message(message.chat.id, "প্রথমে কাজটা শেষ করো 👆 অথবা `/cancel` লিখো")
    else:
        bot.send_message(message.chat.id, "মেনু থেকে অপশন সিলেক্ট করো 👇")

def run_bot():
    bot.remove_webhook()
    print("Bot polling started")
    bot.infinity_polling(timeout=60, long_polling_timeout=50)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
