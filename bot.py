print("Script started")
import os
import random
from threading import Thread
from flask import Flask
import telebot
from telebot import types
from io import BytesIO
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import qrcode

app = Flask(__name__)

@app.route('/')
def home():
    return "Shanu's Magic Bot - 10 Real Tools 🔥"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, skip_pending=True)
user_state = {}

tools = {
    'Banner Creator': "ব্যানার বানোর জন্য টেমপ্লেট সিলেক্ট করো",
    'Eid Rules': "ঈদের নিয়ম-কানুন দেখাচ্ছি",
    'Remove BG': "ছবি পাঠাও, BG রিমুভ করে দেব",
    'Fun Zone': "মজার জোন খুলছে",
    'Story Generator': "গল্পের টপিক লিখো",
    'Poem Generator': "কবিতার বিষয় লিখো",
    'Image→PDF': "ছবি পাঠাও, PDF বানাবো",
    'Text→PDF': "Text লিখো, PDF বানাবো",
    'Sticker': "ছবি পাঠাও, স্টিকার বানাবো",
    'QR Generator': "লিংক বা টেক্সট লিখো"
}

@bot.message_handler(commands=['start', 'cancel'])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(btn) for btn in tools.keys()])
    bot.send_message(chat_id, "🔥 **10টা রিয়েল টুল রেডি** 😎\n`/cancel` লিখে বাতিল করো", reply_markup=markup, parse_mode="Markdown")

def cancel_prev(chat_id):
    if user_state.get(chat_id):
        user_state[chat_id] = None
        bot.send_message(chat_id, "আগের প্রসেস ক্যান্সেল হলো ✅")

# 1. Banner Creator
@bot.message_handler(func=lambda m: m.text == 'Banner Creator')
def banner_start(message):
    cancel_prev(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(f"T{i}", callback_data=f"tpl_{i}") for i in range(1, 7)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ বাতিল", callback_data="tpl_cancel"))
    bot.send_message(message.chat.id, "🎨 6টা টেমপ্লেট থেকে সিলেক্ট করো:", reply_markup=markup)
    user_state[message.chat.id] = 'banner_tpl'

@bot.callback_query_handler(func=lambda call: call.data.startswith('tpl_'))
def banner_tpl_select(call):
    chat_id = call.message.chat.id
    if call.data == 'tpl_cancel':
        bot.edit_message_text("বাতিল", chat_id, call.message.id)
        user_state[chat_id] = None
        return
    user_state[chat_id] = {'state': 'banner_name', 'tpl': call.data.split('_')[1]}
    bot.edit_message_text("✅ টেমপ্লেট সিলেক্ট হলো\nএখন নাম লিখো:", chat_id, call.message.id)

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_name')
def banner_name(message):
    user_state[message.chat.id]['name'] = message.text
    user_state[message.chat.id]['state'] = 'banner_addr'
    bot.send_message(message.chat.id, "ঠিকানা লিখো:")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), dict) and user_state[m.chat.id].get('state') == 'banner_addr')
def banner_addr(message):
    data = user_state[message.chat.id]
    try:
        img = Image.new('RGB', (1080, 1350), color=(25, 25, 112))
        draw = ImageDraw.Draw(img)
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

# 2. Eid Rules
@bot.message_handler(func=lambda m: m.text == 'Eid Rules')
def eid_rules(message):
    cancel_prev(message.chat.id)
    text = """🕌 **ঈদ-উল-ফিতর এর নিয়ম-কানুন**
1️⃣ ঈদের নামাজ: 2 রাকাত, 6 তাকবির
2️⃣ সুন্নত: গোসল, সুন্দর পোশাক, মিষ্টি খেয়ে যাওয়া
3️⃣ ফিতরা: নামাজের আগে দিতে হবে
4️⃣ আদব: সবার সাথে ভালো ব্যবহার, দান করা"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# 3. Remove BG
@bot.message_handler(func=lambda m: m.text == 'Remove BG')
def remove_bg_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'remove_bg'
    bot.send_message(message.chat.id, "🗑️ ছবি পাঠাও")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'remove_bg', content_types=['photo'])
def remove_bg_process(message):
    try:
        downloaded = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        bot.send_message(message.chat.id, "⏳ প্রসেসিং...")
        output = remove(downloaded)
        bot.send_photo(message.chat.id, output, caption="✅ BG রিমুভ কমপ্লিট")
        user_state[message.chat.id] = None
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ এরর: {str(e)}")
        user_state[message.chat.id] = None

# 4. Fun Zone
@bot.message_handler(func=lambda m: m.text == 'Fun Zone')
def fun_zone(message):
    cancel_prev(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('😂 জোকস', '🎲 রিডল', '📚 ফ্যাক্ট', '🔙 ব্যাক')
    bot.send_message(message.chat.id, "🎭 Fun Zone:", reply_markup=markup)
    user_state[message.chat.id] = 'fun_menu'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'fun_menu')
def fun_handler(message):
    jokes = ["শিক্ষক: 2+2=? ছাত্র: 22 স্যার! 😂", "কম্পিউটার: আমি হ্যাং। ইউজার: আমিও!"]
    riddles = ["4 পা আছে কিন্তু হাঁটতে পারি না। কে? উত্তর: টেবিল", "পানিতে ভাসে কিন্তু ডুবে না। কি? উত্তর: বরফ"]
    facts = ["পৃথিবীর সবচেয়ে বড় মরুভূমি সাহারা", "অক্টোপাসের 3টা হার্ট আছে"]
    if message.text == '😂 জোকস':
        bot.send_message(message.chat.id, random.choice(jokes))
        user_state[message.chat.id] = None
    elif message.text == '🎲 রিডল':
        bot.send_message(message.chat.id, random.choice(riddles))
        user_state[message.chat.id] = None
    elif message.text == '📚 ফ্যাক্ট':
        bot.send_message(message.chat.id, random.choice(facts))
        user_state[message.chat.id] = None
    elif message.text == '🔙 ব্যাক':
        user_state[message.chat.id] = None
        start(message)

# 5. Story Generator
@bot.message_handler(func=lambda m: m.text == 'Story Generator')
def story_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'story'
    bot.send_message(message.chat.id, "গল্পের টপিক লিখো। যেমন: বিড়াল, জঙ্গল, স্কুল")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'story')
def story_gen(message):
    topic = message.text
    story = f"একদিন {topic} নিয়ে একটা মজার ঘটনা ঘটলো। সবাই খুব অবাক হলো। শেষে সব ঠিক হয়ে গেলো আর সবাই খুশি হলো। 😊"
    bot.send_message(message.chat.id, f"📖 **গল্প:**\n{story}", parse_mode="Markdown")
    user_state[message.chat.id] = None

# 6. Poem Generator
@bot.message_handler(func=lambda m: m.text == 'Poem Generator')
def poem_start(message):
    cancel_prev(message.chat.id)
    user_state[message.chat.id] = 'poem'
    bot.send_message(message.chat.id, "কবিতার বিষয় লিখো। যেমন: মা, প্রকৃতি, বন্ধু")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'poem')
def poem_gen(message):
    topic = message.text
    poem = f"{topic} তুমি কত সুন্দর\nতোমার তুলনা নাই\nতোমায় নিয়ে লিখতে গেলে\nশব্দ হারিয়ে যায়"
    bot.send_message(message.chat.id, f"✍️ **কবিতা:**\n{poem}", parse_mode="Markdown")
    user_state[message.chat.id] = None

# 7. Image to PDF
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

# 8. Text to PDF
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
