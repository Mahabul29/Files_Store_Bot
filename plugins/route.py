import os, asyncio, humanize
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import START_MSG, FILE_AUTO_DELETE, CUSTOM_CAPTION, PROTECT_CONTENT
from helper_func import subscribed, decode, get_messages

# This links your start.py to the logic in route.py
from plugins.route import send_media_and_handle_delete, RECALL_BUTTON

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    text = message.text
    
    # If the user clicked a link (e.g., /start base64_string)
    if len(text.split()) > 1:
        base64_string = text.split(" ", 1)[1]
        
        try:
            # Step 1: Decode the link
            decoded_string = await decode(base64_string)
            
            # Step 2: Send media and start the 60s timer
            await send_media_and_handle_delete(client, message, decoded_string)
            
        except Exception as e:
            # This prevents the 'Failed to decode' crash from your logs
            return await message.reply_text(f"❌ **Link Error:** {e}")
    
    else:
        # Standard message for a plain /start
        await message.reply_text(
            text=START_MSG.format(first=message.from_user.first_name, id=message.from_user.id),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("About ℹ️", callback_data="about"),
                InlineKeyboardButton("Close ✖️", callback_data="close")
            ]])
        )
        
