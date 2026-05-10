@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🎬 YT Video", callback_data="yt_video")
    btn2 = types.InlineKeyboardButton("🎵 MP3 গান", callback_data="yt_audio")
    btn3 = types.InlineKeyboardButton("🤖 AI Chat", callback_data="ai_chat")
    btn4 = types.InlineKeyboardButton("✍️ ছন্দমালা", callback_data="poem")
    btn5 = types.InlineKeyboardButton("🖼️ Photo Editor", callback_data="photo_edit")
    btn6 = types.InlineKeyboardButton("🎥 Photo→Video", callback_data="photo_video")
    btn7 = types.InlineKeyboardButton("🖼️ QR Code", callback_data="qr")

    # FB_LINK থাকলে বাটন দেখাবে, না থাকলে দেখাবে না
    if FB_LINK:
        btn8 = types.InlineKeyboardButton("📞 Contact Admin", url=FB_LINK)
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    else:
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    bot.send_message(message.chat.id, "🔥 **All-in-One Super Bot** 🔥\n\nকি করতে চাও ভাই?", reply_markup=markup, parse_mode="Markdown")
