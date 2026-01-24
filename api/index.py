import os
from flask import Flask, request
import telebot

# 1. Lowercase "import" and use threaded=False for serverless stability
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

app = Flask(__name__)

# 2. Route to receive updates from Telegram
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid Content-Type", 403

# 3. Route to set the webhook (Run this once in your browser)
@app.route("/")
def webhook():
    bot.remove_webhook()
    # Vercel provides VERCEL_URL automatically
    domain = os.getenv("VERCEL_URL") 
    bot.set_webhook(url=f"https://{domain}/{BOT_TOKEN}")
    return "Webhook successfully set!", 200

# Bot logic example
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Your bot is successfully running on Vercel.")

# Add your other bot handlers here...
