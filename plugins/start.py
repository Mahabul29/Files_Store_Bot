import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait

# --- CONFIGURATION ---
# These should ideally be in a config.py or environment variables
API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    # Check if the start command has a parameter (like a file link/ID)
    if len(message.command) > 1:
        data = message.command[1]
        await message.reply_text(
            "**Processing your request...**\n\nI am retrieving your file. Please wait.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Click Here to Get File", callback_data=f"get_{data}")]
            ])
        )
    else:
        # Standard welcome message
        welcome_text = (
            f"Hello {message.from_user.mention}!\n\n"
            "I am a File Management Bot. Send me a valid file link to get started!\n\n"
            "**Features:**\n"
            "• Auto-delete messages for privacy\n"
            "• High-speed file processing"
        )
        await message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Channel", url="https://t.me/your_channel"),
                 InlineKeyboardButton("Support", url="https://t.me/your_admin")]
            ])
        )

@app.on_message(filters.private & filters.text)
async def handle_links(client, message):
    # Logic to handle shared links or text
    if "t.me/" in message.text:
        sent_msg = await message.reply_text("✅ Link received! Generating your secure access button...")
        
        # Example of the 'Click Here' button you saw
        await sent_msg.edit_text(
            "**File is ready!**\n\nThis message will be self-destructed in 60 seconds to protect privacy.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Click Here", url=message.text)]
            ])
        )
        
        # Auto-delete logic
        await asyncio.sleep(60)
        try:
            await sent_msg.delete()
            await message.delete()
        except Exception as e:
            print(f"Error during deletion: {e}")
    else:
        await message.reply_text("Please send a valid Telegram file link.")

# Error handling for FloodWait (Telegram's 420 error)
@app.on_message(filters.all)
async def flood_handler(client, message):
    try:
        pass # Normal processing
    except FloodWait as e:
        await asyncio.sleep(e.value)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
    
