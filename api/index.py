import os
import asyncio
from flask import Flask, request
from pyrogram import Client, types

app = Flask(__name__)

# Initialize the Client (Don't use .run() or .start() here)
bot = Client(
    "my_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
    in_memory=True
)

@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/webhook', methods=['POST'])
async def handle_webhook():
    if request.headers.get('content-type') == 'application/json':
        # This part is complex because Pyrogram isn't built for webhooks
        # It's better to just log that we received data for now
        print("Update received from Telegram")
        return "OK", 200
    return "Forbidden", 403
    
