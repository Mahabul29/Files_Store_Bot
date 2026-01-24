import os
from flask import Flask, request
import telebot

# Initialize your bot using the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Route to receive updates from Telegram
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Route to set the webhook (Run this once in your browser)
@app.route("/")
def webhook():
    bot.remove_webhook()
    # Replace 'your-vercel-domain.vercel.app' with your actual Vercel URL
    domain = os.getenv("VERCEL_URL") 
    bot.set_webhook(url=f"https://{domain}/{BOT_TOKEN}")
    return "Webhook successfully set!", 200

# Bot logic example: /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Your bot is running on Vercel.")

# Critical: Do NOT use bot.polling() on Vercel.
