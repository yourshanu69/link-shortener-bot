import telebot
import random
import os
import io
from googletrans import Translator
from fpdf import FPDF
from gtts import gTTS

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
translator = Translator()

user_state = {}

# Vocab লোড - 500+ ওয়ার্ড সাপোর্ট
def load_vocab():
    vocab = []
    try:
        with open('vocab.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line and len(line.split('|')) >= 3:
                    parts = line.split('|', 2)
                    vocab.append(parts)
    except Exception as e:
        print(f"Vocab load error: {e}")
    return vocab

vocab_list = load_vocab()
print(f"Loaded {len(vocab_list)} words from vocab.txt")

@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = None
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add('📚 Word of the Day', '🌐 Auto Translate')
    markup.add('😄 Fun Zone', '📄 Text to PDF')
    markup.add('🔊 TTS Voice', '📝 Grammar Check')
    markup.add('🎯 Quiz', '📖 Story Mode')
    markup.add('🎤 Pronunciation', '📊 Progress')
    markup.add('🎧 Listening', '✍️ Writing')
    markup.add('🗣️ Speaking', '📅 Daily Plan')
    markup.add('🎮 Game', '💡 Tips')
    markup.add('🔔 Reminder', '⚙️ Settings', '❓ Help')

    bot.send_message(
        message.chat.id,
        f"সালাম ভাই! Spoken English Bot 👋\n\n{len(vocab_list)}টা ওয়ার্ড লোড হইছে ✅\nনিচ থেকে বাটন চাপো:",
        reply_markup=markup
    )

# 1. Word of the Day - তোমার 500+ vocab থেকে র‍্যান্ডম
@bot.message_handler(func=lambda m: m.text == '📚 Word of the Day')
def send_word(message):
    if not vocab_list:
        bot.reply_to(message, "ভাই vocab.txt ফাঁকা। ওয়ার্ড অ্যাড করো")
        return
    word, meaning, example = random.choice(vocab_list)
    text = f"**📚 Spoken Word**\n\n**Word:** `{word}`\n**Meaning:** {meaning}\n**Example:** {example}"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# 2. Auto Translate - রিয়েল Google Translate
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "translate")
def auto_translate(message):
    if message.text == "/cancel":
        user_state[message.chat.id] = None
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('📚 Word of the Day', '🌐 Auto Translate')
        bot.send_message(message.chat.id, "Translate বন্ধ ✅", reply_markup=markup)
        return
    try:
        result = translator.translate(message.text, dest='en')
        bot.send_message(
            message.chat.id,
            f"**তুমি:** {message.text}\n**ইংরেজি:** `{result.text}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"সরি ভাই এরর: {str(e)}")

@bot.message_handler(func=lambda m: m.text == '🌐 Auto Translate')
def btn_translate(message):
    user_state[message.chat.id] = "translate"
    bot.send_message(message.chat.id, "🌐 Auto Translate ON\nবাংলা লিখো, ইংরেজি পাবা। বন্ধ: /cancel")

# 3. Fun Zone - রিয়েল কন্টেন্ট
@bot.message_handler(func=lambda m: m.text == '😄 Fun Zone')
def fun_zone(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('😂 জোকস', '🧩 রিডল', '🎤 ফ্যাক্ট', '⬅️ ব্যাক')
    bot.send_message(message.chat.id, "😄 Fun Zone:", reply_markup=markup)
    user_state[message.chat.id] = 'fun_menu'

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'fun_menu')
def fun_handler(message):
    jokes = ["টিচার: 2+2? স্টুডেন্ট: 22 স্যার! টিচার: বাহ!", "ডাক্তার: রাতে ঘুমাও না কেন? রোগী: স্যার দিনে ঘুমাই!"]
    riddles = ["আমার পা নাই তবু দৌড়াই, মুখ নাই তবু চিৎকার করি। কে? উত্তর: বাতাস", "সবসময় আসে কিন্তু কখনো পৌঁছায় না। কে? উত্তর: আগামীকাল"]
    facts = ["মধু কখনো নষ্ট হয় না। 3000 বছরের পুরান মধুও খাওয়া যায়", "মানুষের DNA এর 50% কলার সাথে মিলে"]
    txt = message.text
    if 'জোকস' in txt: bot.send_message(message.chat.id, random.choice(jokes))
    elif 'রিডল' in txt: bot.send_message(message.chat.id, random.choice(riddles))
    elif 'ফ্যাক্ট' in txt: bot.send_message(message.chat.id, random.choice(facts))
    elif 'ব্যাক' in txt: start(message); user_state[message.chat.id] = None

# 4. Text to PDF - রিয়েল PDF বানাবে
@bot.message_handler(func=lambda m: m.text == '📄 Text to PDF')
def pdf_start(message):
    user_state[message.chat.id] = 'pdf_wait'
    bot.send_message(message.chat.id, "PDF বানাতে টেক্সট পাঠাও:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'pdf_wait')
def pdf_create(message):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, message.text)
    pdf_file = io.BytesIO()
    pdf.output(pdf_file)
    pdf_file.seek(0)
    bot.send_document(message.chat.id, pdf_file, visible_file_name="spoken_english.pdf")
    user_state[message.chat.id] = None

# 5. TTS Voice - রিয়েল ভয়েস
@bot.message_handler(func=lambda m: m.text == '🔊 TTS Voice')
def tts_start(message):
    user_state[message.chat.id] = 'tts_wait'
    bot.send_message(message.chat.id, "কি বলবো ইংরেজিতে লিখে পাঠাও:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'tts_wait')
def tts_create(message):
    tts = gTTS(text=message.text, lang='en')
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    bot.send_audio(message.chat.id, audio_file)
    user_state[message.chat.id] = None

# 6. Grammar Check - বেসিক
@bot.message_handler(func=lambda m: m.text == '📝 Grammar Check')
def grammar_check(message):
    user_state[message.chat.id] = 'grammar_wait'
    bot.send_message(message.chat.id, "ইংরেজি সেন্টেন্স পাঠাও, আমি চেক করবো:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == 'grammar_wait')
def grammar_process(message):
    text = message.text
    tips = []
    if not text[0].isupper(): tips.append("প্রথম অক্ষর Capital হবে")
    if not text.endswith('.'): tips.append("শেষে. দাও")
    if tips: bot.send_message(message.chat.id, "টিপস:\n" + "\n".join(tips))
    else: bot.send_message(message.chat.id, "Perfect! ✅")
    user_state[message.chat.id] = None

# 7. Quiz - vocab থেকে
@bot.message_handler(func=lambda m: m.text == '🎯 Quiz')
def quiz_start(message):
    if not vocab_list: bot.send_message(message.chat.id, "Vocab নাই ভাই"); return
    word, meaning, _ = random.choice(vocab_list)
    user_state[message.chat.id] = {'quiz': meaning, 'word': word}
    bot.send_message(message.chat.id, f"Meaning কি? `{meaning}`", parse_mode='Markdown')

@bot.message_handler(func=lambda m: 'quiz' in user_state.get(m.chat.id, {}))
def quiz_check(message):
    data = user_state[message.chat.id]
    if message.text.lower() == data['word'].lower():
        bot.send_message(message.chat.id, f"সঠিক! ✅ Word: {data['word']}")
    else:
        bot.send_message(message.chat.id, f"ভুল 😅 সঠিক: {data['word']}")
    user_state[message.chat.id] = None

# 8-19. বাকিগুলা - ফুল ফিচার পরে অ্যাড করবা। আপাতত বেসিক রেসপন্স
for btn in ['📖 Story Mode', '🎤 Pronunciation', '📊 Progress', '🎧 Listening',
            '✍️ Writing', '🗣️ Speaking', '📅 Daily Plan', '🎮 Game',
            '💡 Tips', '🔔 Reminder', '⚙️ Settings', '❓ Help']:
    @bot.message_handler(func=lambda m, b=btn: m.text == b)
    def other_features(message, b=btn):
        bot.send_message(message.chat.id, f"{b} ফিচার আপডেট আসতেছে 🚀\nআপাতত Word + Translate + PDF + TTS + Quiz ইউজ করো")

print("Bot running...")
bot.polling(none_stop=True)
