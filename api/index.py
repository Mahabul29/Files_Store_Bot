import os
from flask import Flask, request
import telebot

# Get your token from Vercel Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

app = Flask(__name__)

# This handles the main URL (https://your-bot.vercel.app/)
@app.route('/')
def index():
    return "Bot is awake!", 200

# This handles the Telegram Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

# Command handler
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Your bot is working on Vercel.")
    
