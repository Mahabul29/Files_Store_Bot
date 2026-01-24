import os
import asyncio
from flask import Flask, request
from pyrogram import Client, types

app = Flask(__name__)

# Use your actual Environment Variables from Vercel Settings
bot = Client(
    "my_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
    in_memory=True
)

@app.route('/')
def home():
    return "Bot is Alive!", 200

@app.route('/webhook', methods=['POST'])
async def handle_webhook():
    # This wakes up the bot for 10 seconds to process the message
    if request.headers.get('content-type') == 'application/json':
        update = await request.get_json()
        print(f"Received update: {update}")
        return "OK", 200
    return "Forbidden", 403
    
