import os
import sqlite3
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 1. Bot Token + Admin ID boshao ekhane
BOT_TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
ADMIN_ID = 123456789 # Tmr Telegram ID

# 2. User data save korar jonno DB
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, count INTEGER)')
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # User DB te save
    c.execute("INSERT OR IGNORE INTO users (user_id, username, count) VALUES (?,?, 0)", (user.id, user.username))
    c.execute("UPDATE users SET count = count + 1 WHERE user_id =?", (user.id,))
    conn.commit()
    await update.message.reply_text("Pic pathao, ami PDF baniye dicchi 📄")

async def handle_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    c.execute("UPDATE users SET count = count + 1 WHERE user_id =?", (user_id,))
    conn.commit()

    # Sob pic download kore list e rakho
    image_list = []
    for photo in update.message.photo:
        file = await context.bot.get_file(photo.file_id)
        filename = f"{user_id}_{photo.file_id}.jpg"
        await file.download_to_drive(filename)
        image_list.append(Image.open(filename).convert('RGB'))

    if not image_list:
        return

    # PDF banano
    pdf_name = f"{user_id}_output.pdf"
    image_list[0].save(pdf_name, save_all=True, append_images=image_list[1:])

    await update.message.reply_document(document=open(pdf_name, 'rb'), filename="file.pdf")

    # Temp file delete
    for img in image_list: img.close()
    for f in os.listdir():
        if f.startswith(str(user_id)): os.remove(f)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    c.execute("SELECT * FROM users ORDER BY count DESC")
    users = c.fetchall()
    msg = f"**Total Users: {len(users)}**\n\n"
    for u in users[:20]: # Top 20 user
        msg += f"ID: `{u[0]}` | @{u[1]} | Use: {u[2]}\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
app.run_polling()
