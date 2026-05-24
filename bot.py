print("Script started")
import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types
from io import BytesIO
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)

@app.route('/')
def home():
    return "Shanu's Magic Bot - All Real Tools 🔥"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, skip_pending=True)
user_state = {}

tools = {
    'Banner Creator': "ব্যানার বানোর জন্য টেমপ্লেট সিলেক্ট করো",
    'Eid Rules': "ঈদের নিয়ম-কানুন দেখাচ্ছি",
    'Eid Greeting': "কার জন্য শুভেচ্ছা বানাবা?",
    'Fun Zone': "মজার জোন খুলছে",
    'Remove BG': "ছবি পাঠাও, BG রিমুভ করে দেব",
    'Image→PDF': "ছবি পাঠাও, PDF বানাবো",
    'Text→PDF': "Text লিখো, PDF বানাবো",
    'Sticker': "ছবি পাঠাও, স্টিকার বানাবো"
}

@bot.message_handler(commands=['start', 'cancel'])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = None

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(btn) for btn in tools.keys()])

    bot.send_message(chat_id, "🔥 **8টা রিয়েল টুল রেডি** 😎\n\n"
                     "1. Banner Creator - ব্যানার বানাও\n"
                     "2. Eid Rules - ঈদের নিয়ম\n"
                     "3. Eid Greeting - শুভেচ্ছা বানাও\n"
                     "4. Fun Zone - জোকস/রিডল\n"
                     "5. Remove BG - BG রিমুভ\n"
                     "6. Image→PDF - ছবি দিয়ে PDF\n"
                     "7. Text→PDF - টেক্সট দিয়ে PDF\n"
                     "8. Sticker - ছবি থেকে স্টিকার\n"
                     "`/cancel` লিখে বাতিল করো",
                     reply_markup=markup, parse_mode="Markdown")

def cancel_prev(chat_id):
    if user_state.get(chat_id):
        user_state[chat_id] = None
        bot.send_message(chat_id, "আগের প্রসেস ক্যান্সেল হলো ✅")

# ====== 1. Banner Creator - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Banner Creator')
def banner_start(message):
    cancel_prev(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(f"Template {i}", callback_data=f"tpl_{i}") for i in range(1, 7)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ বাতিল", callback_data="tpl_cancel"))
    bot.send_message(message.chat.id, "🎨 6টা টেমপ্লেট থেকে একটা সিলেক্ট করো:", reply_markup=markup)
    user_state[message.chat.id] = 'banner_tpl'

@bot.callback_query_handler(func=lambda call: call.data.startswith('tpl_'))
def banner_tpl_select(call):
    chat_id = call.message.chat.id
    if call.data == 'tpl_cancel':
        bot.edit_message_text("বাতিল", chat_id, call.message.id)
        user_state[chat_id] = None
        return

    tpl_num = call.data.split('_')[1]
    user_state[chat_id] = {'state': 'banner_name', 'tpl': tpl_num}
    bot.edit_message_text(f"✅ Template {tpl_num} সিলেক্ট হলো\nএখন নাম লিখো:", chat_id, call.message.id)

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_name')
def banner_name(message):
    user_state[message.chat.id]['name'] = message.text
    user_state[message.chat.id]['state'] = 'banner_addr'
    bot.send_message(message.chat.id, "ঠিকানা লিখো:")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_addr')
def banner_addr(message):
    data = user_state[message.chat.id]
    try:
        # Simple banner generation
        img = Image.new('RGB', (1080, 1350), color=(25, 25, 112))
        draw = ImageDraw.Draw(img)

        # Try to use default font
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text((540, 500), data['name'], font=font_big, fill=(255, 215, 0), anchor="mm")
        draw.text((540, 650), message.text, font=font_small, fill=(255, 255, 255), anchor="mm")
        draw.text((540, 750), f"Template {data['tpl']}", font=font_small, fill=(200, 200, 200), anchor="mm")

        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        bot.send_photo(message.chat.id, buf, caption="✅ ব্যানার রেডি!")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

# ====== 2. Eid Rules - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Eid Rules')
def eid_rules(message):
    cancel_prev(message.chat.id)
    text = """🕌 **ঈদ-উল-ফিতর এর নিয়ম-কানুন**

1️⃣ **ঈদের নামাজ**
   - 2 রাকাত ওয়াজিব নামাজ
   - 6 তাকবির: প্রথম রাকাতে 3টা, দ্বিতীয় রাকাতে 3টা

2️⃣ **সুন্নত আমল**
   - ফজরের পর গোসল করা
   - সুন্দর পোশাক পরা
   - মিষ্টি খেয়ে নামাজে যাওয়া
   - তাকবির পড়া: আল্লাহু আকবার

3️⃣ **ফিতরা**
   - নামাজের আগে ফিতরা দিতে হবে
   - জনপ্রতি 2.5 কেজি খাবার বা সমমূল্য টাকা

4️⃣ **আদব**
   - হাসিমুখে সবার সাথে দেখা করা
   - গরিব-দুঃখীর খোঁজ নেওয়া
   - আত্মীয়-স্বজনের সাথে যোগাযোগ"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ====== 3. Eid Greeting - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Eid Greeting')
def eid_greeting(message):
    cancel_prev(message.chat.id)
    bot.send_message(message.chat.id, "কার জন্য শুভেচ্ছা বানাবো? নাম লিখো:")
    user_state[message.chat.id] = 'greeting_name'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'greeting_name')
def greeting_name(message):
    name = message.text
    greetings = [
        f"🌙 ঈদ মোবারক {name}! আল্লাহ তোমার জীবন সুখে ভরে দিক 🎉",
        f"✨ {name}, তোমাকে এবং তোমার পরিবারকে ঈদের শুভেচ্ছা! ❤️",
        f"🕌 ঈদ-উল-ফিতর মোবারক {name}! আল্লাহ কবুল করুক 🌟"
    ]
    import random
    bot.send_message(message.chat.id, random.choice(greetings))
    user_state[message.chat.id] = None

# ====== 4. Fun Zone - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Fun Zone')
def fun_zone(message):
    cancel_prev(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('😂 জোকস', '🎲 রিডল', '📚 জেনারেল নলেজ', '🔙 ব্যাক')
    bot.send_message(message.chat.id, "🎭 Fun Zone এ স্বাগতম:", reply_markup=markup)
    user_state[message.chat.id] = 'fun_menu'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'fun_menu')
def fun_handler(message):
    jokes = [
        "শিক্ষক: 2+2=? ছাত্র: 22 স্যার! 😂",
        "কম্পিউটার: আমি হ্যাং হয়ে গেছি। ইউজার: আমিও!",
        "বউ: আমি মোটা? স্বামী: না, তুমি গোলাকার!"
    ]
    riddles = [
        "প্রশ্ন: 4 পা আছে কিন্তু হাঁটতে পারি না। আমি কে?\nউত্তর: টেবিল",
        "প্রশ্ন: পানিতে ভাসে কিন্তু ডুবে না। কি?\nউত্তর: বরফ",
        "প্রশ্ন: মাথা আছে কিন্তু মগজ নাই। কি?\nউত্তর: পুতুল"
    ]
    facts = [
        "📚 পৃথিবীর সবচেয়ে বড় মরুভূমি সাহারা",
        "📚 অক্টোপাসের 3টা হার্ট আছে",
        "📚 মানুষের শরীরে 206টা হাড় আছে"
    ]

    import random
    if message.text == '😂 জোকস':
        bot.send_message(message.chat.id, random.choice(jokes))
        user_state[message.chat.id] = None
    elif message.text == '🎲 রিডল':
        bot.send_message(message.chat.id, random.choice(riddles))
        user_state[message.chat.id] = None
    elif message.text == '📚 জেনারেল নলেজ':
        bot.send_message(message.chat.id, random.choice(facts))
        user_state[message.chat.id] = None
    elif message.text == '🔙 ব্যাক':
        user_state[message.chat.id] = None
        start(message)

# ====== 5. Remove BG - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Remove BG')
def remove_bg_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'remove_bg'
    bot.send_message(message.chat.id, "🗑️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'remove_bg', content_types=['photo'])
def remove_bg_process(message):
    try:
        file_id = message.photo[-1].file_id
        downloaded = bot.download_file(bot.get_file(file_id).file_path)
        bot.send_message(message.chat.id, "⏳ প্রসেসিং...")
        output = remove(downloaded)
        bot.send_photo(message.chat.id, output, caption="✅ BG রিমুভ কমপ্লিট")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

# ====== 6. Image to PDF - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Image→PDF')
def img_to_pdf_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = {'state': 'img_pdf', 'images': []}
    bot.send_message(message.chat.id, "📷 ছবি পাঠাও। শেষে 'Done' লিখো")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'img_pdf', content_types=['photo', 'text'])
def img_to_pdf_process(message):
    if message.text == 'Done':
        images = user_state[message.chat.id]['images']
        if not images:
            bot.send_message(message.chat.id, "কোনো ছবি পাই নাই")
            user_state[message.chat.id] = None
            return
        try:
            bot.send_message(message.chat.id, "⏳ PDF বানাচ্ছি...")
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
        bot.send_message(message.chat.id, f"✅ {len(user_state[message.chat.id]['images'])} টা ছবি যোগ হলো")

# ====== 7. Text to PDF - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Text→PDF')
def txt_to_pdf_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'txt_pdf'
    bot.send_message(message.chat.id, "📝 Text লিখো")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'txt_pdf')
def txt_to_pdf_process(message):
    try:
        c = canvas.Canvas('/tmp/text.pdf', pagesize=A4)
        textobject = c.beginText(100, 800)
        for line in message.text.split('\n'):
            textobject.textLine(line)
        c.drawText(textobject)
        c.save()
        with open('/tmp/text.pdf', 'rb') as f:
            bot.send_document(message.chat.id, f, caption="✅ PDF রেডি")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

# ====== 8. Sticker - REAL ======
@bot.message_handler(func=lambda m: m.text == 'Sticker')
def sticker_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'sticker'
    bot.send_message(message.chat.id, "🖼️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'sticker', content_types=['photo'])
def sticker_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        img = Image.open(BytesIO(downloaded)).resize((512, 512), Image.Resampling.LANCZOS)
        img.save('/tmp/sticker.webp', 'WEBP')
        with open('/tmp/sticker.webp', 'rb') as f:
            bot.send_sticker(message.chat.id, f)
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document'])
def handle_default(message):
    if user_state.get(message.chat.id):
        bot.send_message(message.chat.id, "প্রথমে কাজটা শেষ করো 👆 অথবা `/cancel` লিখো")
    else:
        bot.send_message(message.chat.id, "মেনু থেকে একটা অপশন সিলেক্ট করো 👇")

def run_bot():
    bot.remove_webhook()
    print("Bot polling started")
    bot.infinity_polling(timeout=60, long_polling_timeout=50)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
