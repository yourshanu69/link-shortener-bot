import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('BOT_TOKEN')
OUO_API_KEY = os.environ.get('OUO_KEY')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔗 Link Shortener Bot এ স্বাগতম\n\n"
        "আমাকে যেকোনো লিংক পাঠাও। আমি ছোট লিংক বানায় দিবো।"
    )

async def short_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_link = update.message.text
    if not user_link.startswith("http"):
        await update.message.reply_text("ভাই সঠিক লিংক দাও। http:// দিয়ে শুরু হতে হবে")
        return
    
    api_url = f"https://ouo.io/api/{OUO_API_KEY}?s={user_link}"
    response = requests.get(api_url).text
    
    if "http" in response:
        await update.message.reply_text(f"✅ Short Link Ready!\n\n🔗 {response}")
    else:
        await update.message.reply_text("Error! API Key ঠিক আছে কিনা দেখো।")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, short_link))

print("Bot Started... ✅")
app.run_polling()
