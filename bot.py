import os
import telebot
import requests
import replicate
from google import genai
from google.genai import types
from telebot import types as tele_types
from pytube import YouTube, Search
import tempfile
import qrcode
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REMOVE_BG_KEY = os.getenv("REMOVE_BG_KEY")
REPLICATE_TOKEN = os.getenv("REPLICATE_TOKEN")
WEATHER_API = os.getenv("WEATHER_API")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)
if REPLICATE_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

user_state = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = tele_types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = tele_types.KeyboardButton("🎬 YT Video")
    btn2 = tele_types.KeyboardButton("🎵 MP3 গান")
    btn3 = tele_types.KeyboardButton("🤖 AI Chat")
    btn4 = tele_types.KeyboardButton("✍️ ছন্দমালা")
    btn5 = tele_types.KeyboardButton("🖼️ Photo Editor")
    btn6 = tele_types.KeyboardButton("🎥 Photo→Video")
    btn7 = tele_types.KeyboardButton("🖼️ QR Code")
    btn8 = tele_types.KeyboardButton("📱 Insta Reel")
    btn9 = tele_types.KeyboardButton("🌤️ Weather")
    btn10 = tele_types.KeyboardButton("🌐 Translate")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    bot.send_message(message.chat.id, "🔥 **All-in-One Super Bot 10-in-1** 🔥\n\nনিচের কিবোর্ড থেকে সিলেক্ট করো বা / চেপে Menu দেখো 👇", reply_markup=markup)

@bot.message_handler(commands=['ytvideo', 'ytaudio', 'aichat', 'poem', 'photoedit', 'photovideo', 'qrcode', 'insta', 'weather', 'translate'])
def command_handler(message):
    chat_id = message.chat.id
    cmd = message.text[1:]
    if cmd == "ytvideo": user_state[chat_id] = "yt_video"; bot.send_message(chat_id, "🎬 YouTube ভিডিওর লিংক দাও:")
    elif cmd == "ytaudio": user_state[chat_id] = "yt_audio"; bot.send_message(chat_id, "🎵 গানের নাম বা YouTube লিংক দাও:")
    elif cmd == "aichat": user_state[chat_id] = "ai_chat"; bot.send_message(chat_id, "🤖 আমাকে যেকোনো প্রশ্ন করো:")
    elif cmd == "poem": user_state[chat_id] = "poem"; bot.send_message(chat_id, "✍️ বয়স কত? লিখো: `বয়স 20, প্রেমের কবিতা`")
    elif cmd == "photoedit": user_state[chat_id] = "photo_edit"; bot.send_message(chat_id, "🖼️ ছবি পাঠাও। Background Remove করে দিবো:")
    elif cmd == "photovideo": user_state[chat_id] = "photo_video"; bot.send_message(chat_id, "🎥 ছবি পাঠাও। আমি ভিডিও বানায় দিবো:")
    elif cmd == "qrcode": user_state[chat_id] = "qr"; bot.send_message(chat_id, "🖼️ QR এর জন্য লেখা বা লিংক দাও:")
    elif cmd == "insta": user_state[chat_id] = "insta"; bot.send_message(chat_id, "📱 Instagram Reel/Post এর লিংক দাও:")
    elif cmd == "weather": user_state[chat_id] = "weather"; bot.send_message(chat_id, "🌤️ শহরের নাম লিখো: `Dhaka`")
    elif cmd == "translate": user_state[chat_id] = "translate"; bot.send_message(chat_id, "🌐 যেকোনো ভাষায় লিখো। আমি বাংলা/ইংলিশে ট্রান্সলেট করে দিবো:")

@bot.message_handler(func=lambda message: True)
def handle_keyboard(message):
    chat_id = message.chat.id
    text = message.text
    state = user_state.get(chat_id)

    if text == "🎬 YT Video": user_state[chat_id] = "yt_video"; bot.send_message(chat_id, "🎬 YouTube ভিডিওর লিংক দাও:"); return
    elif text == "🎵 MP3 গান": user_state[chat_id] = "yt_audio"; bot.send_message(chat_id, "🎵 গানের নাম বা YouTube লিংক দাও:"); return
    elif text == "🤖 AI Chat": user_state[chat_id] = "ai_chat"; bot.send_message(chat_id, "🤖 আমাকে যেকোনো প্রশ্ন করো:"); return
    elif text == "✍️ ছন্দমালা": user_state[chat_id] = "poem"; bot.send_message(chat_id, "✍️ বয়স কত? লিখো: `বয়স 20, প্রেমের কবিতা`"); return
    elif text == "🖼️ Photo Editor": user_state[chat_id] = "photo_edit"; bot.send_message(chat_id, "🖼️ ছবি পাঠাও। Background Remove করে দিবো:"); return
    elif text == "🎥 Photo→Video": user_state[chat_id] = "photo_video"; bot.send_message(chat_id, "🎥 ছবি পাঠাও। আমি ভিডিও বানায় দিবো:"); return
    elif text == "🖼️ QR Code": user_state[chat_id] = "qr"; bot.send_message(chat_id, "🖼️ QR এর জন্য লেখা বা লিংক দাও:"); return
    elif text == "📱 Insta Reel": user_state[chat_id] = "insta"; bot.send_message(chat_id, "📱 Instagram Reel/Post এর লিংক দাও:"); return
    elif text == "🌤️ Weather": user_state[chat_id] = "weather"; bot.send_message(chat_id, "🌤️ শহরের নাম লিখো: `Dhaka`"); return
    elif text == "🌐 Translate": user_state[chat_id] = "translate"; bot.send_message(chat_id, "🌐 যেকোনো ভাষায় লিখো। আমি বাংলা/ইংলিশে ট্রান্সলেট করে দিবো:"); return

    try:
        if state == "yt_video" and message.text:
            msg = bot.send_message(chat_id, "⏳ ডাউনলোড হচ্ছে...")
            yt = YouTube(message.text)
            stream = yt.streams.get_highest_resolution()
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                stream.download(filename=tmp.name)
                bot.send_video(chat_id, open(tmp.name, 'rb'), caption=f"✅ {yt.title}")
            os.remove(tmp.name)
            bot.delete_message(chat_id, msg.message_id)

        elif state == "yt_audio" and message.text:
            msg = bot.send_message(chat_id, "⏳ MP3 বানাচ্ছি...")
            if "youtube.com" in message.text or "youtu.be" in message.text:
                yt = YouTube(message.text)
            else:
                s = Search(message.text)
                yt = s.results[0]
            stream = yt.streams.filter(only_audio=True).first()
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                stream.download(filename=tmp.name)
                bot.send_audio(chat_id, open(tmp.name, 'rb'), title=yt.title)
            os.remove(tmp.name)
            bot.delete_message(chat_id, msg.message_id)

        elif state == "ai_chat" and message.text:
            msg = bot.send_message(chat_id, "🤖 ভাবতেছি...")
            try:
                response = client.models.generate_content(model="gemini-1.5-flash", contents=f"তুমি বন্ধুর মতো কথা বলো। ইউজার: {message.text}")
                bot.edit_message_text(response.text, chat_id, msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Gemini Error: {str(e)}", chat_id, msg.message_id)

        elif state == "poem" and message.text:
            msg = bot.send_message(chat_id, "✍️ কবিতা লিখতেছি...")
            try:
                response = client.models.generate_content(model="gemini-1.5-flash", contents=f"তুমি একজন কবি। {message.text} এই বয়স অনুযায়ী সুন্দর ছন্দমালা/গীতিমালা লিখো। 4-6 লাইন।")
                bot.edit_message_text(response.text, chat_id, msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Gemini Error: {str(e)}", chat_id, msg.message_id)

        elif state == "qr" and message.text:
            img = qrcode.make(message.text)
            bio = BytesIO()
            bio.name = 'qr.jpeg'
            img.save(bio, 'JPEG')
            bio.seek(0)
            bot.send_photo(chat_id, bio, caption="✅ QR Code Ready")

        elif state == "insta" and message.text:
            msg = bot.send_message(chat_id, "⏳ Insta ভিডিও ডাউনলোড হচ্ছে...")
            api_url = f"https://api.safone.dev/instadl?url={message.text}"
            r = requests.get(api_url).json()
            if r['status'] == 200:
                video_url = r['data'][0]['url']
                bot.send_video(chat_id, video_url, caption="✅ Instagram Video Done")
            else:
                bot.send_message(chat_id, "❌ লিংক ভুল বা Private Account")
            bot.delete_message(chat_id, msg.message_id)

        elif state == "weather" and message.text:
            msg = bot.send_message(chat_id, "🌤️ আবহাওয়া চেক করতেছি...")
            city = message.text
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric&lang=bn"
            r = requests.get(url).json()
            if r['cod'] == 200:
                temp = r['main']['temp']
                desc = r['weather'][0]['description']
                humidity = r['main']['humidity']
                text = f"🌤️ **{city} এর আবহাওয়া**\n\n🌡️ তাপমাত্রা: {temp}°C\n☁️ অবস্থা: {desc}\n💧 আদ্রতা: {humidity}%"
                bot.edit_message_text(text, chat_id, msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ শহরের নাম ভুল", chat_id, msg.message_id)

        elif state == "translate" and message.text:
            msg = bot.send_message(chat_id, "🌐 ট্রান্সলেট করতেছি...")
            try:
                response = client.models.generate_content(model="gemini-1.5-flash", contents=f"এই লেখাটা যদি ইংলিশ হয় বাংলায়, আর বাংলা হলে ইংলিশে ট্রান্সলেট করো: {message.text}")
                bot.edit_message_text(f"🌐 **Translation:**\n\n{response.text}", chat_id, msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Gemini Error: {str(e)}", chat_id, msg.message_id)

        user_state[chat_id] = None

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}\nআবার /start দাও")
        user_state[chat_id] = None

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    try:
        if state == "photo_edit":
            file_info = bot.get_file(message.photo[-1].file_id)
            img_data = bot.download_file(file_info.file_path)
            msg = bot.send_message(chat_id, "⏳ Background Remove করতেছি...")
            r = requests.post('https://api.remove.bg/v1.0/removebg', files={'image_file': img_data}, data={'size': 'auto'}, headers={'X-Api-Key': REMOVE_BG_KEY})
            if r.status_code == 200:
                bot.send_photo(chat_id, r.content, caption="✅ BG Remove Done")
            else:
                bot.send_message(chat_id, "❌ Error! API Key চেক করো")
            bot.delete_message(chat_id, msg.message_id)

        elif state == "photo_video":
            file_info = bot.get_file(message.photo[-1].file_id)
            img_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
            msg = bot.send_message(chat_id, "🎥 ভিডিও বানাচ্ছি... 1 মিনিট লাগবে")
            output = replicate.run("stability-ai/stable-video-diffusion:3f0457e4619daac51203dedfad6e7", input={"input_image": img_url, "video_length": "14_frames_with_svd", "fps": 6})
            bot.send_video(chat_id, output, caption="✅ ছবি থেকে ভিডিও Done")
            bot.delete_message(chat_id, msg.message_id)

        user_state[chat_id] = None
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

from telebot.types import BotCommand
commands = [
    BotCommand("start", "বট চালু করো"),
    BotCommand("ytvideo", "YouTube ভিডিও ডাউনলোড"),
    BotCommand("ytaudio", "MP3 গান ডাউনলোড"),
    BotCommand("aichat", "AI এর সাথে কথা বলো"),
    BotCommand("poem", "ছন্দমালা/কবিতা লিখো"),
    BotCommand("photoedit", "ছবির Background Remove"),
    BotCommand("photovideo", "ছবি থেকে ভিডিও বানাও"),
    BotCommand("qrcode", "QR Code বানাও"),
    BotCommand("insta", "Instagram Reel ডাউনলোড"),
    BotCommand("weather", "আবহাওয়া দেখো"),
    BotCommand("translate", "যেকোনো ভাষা ট্রান্সলেট"),
]
bot.set_my_commands(commands)

bot.infinity_polling()
