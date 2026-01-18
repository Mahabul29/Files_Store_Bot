import os, asyncio, humanize, time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE,
    START_PIC
)
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, present_user

# --- SETUP ---
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    """The Start command provides files directly and immediately."""
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass
            
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        
        # --- DIRECT FILE DELIVERY ---
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            ids = range(start, end + 1) if start <= end else []
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        else:
            return

        temp_msg = await message.reply("<b>Processing your request...</b>")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong fetching files.")
            return
        await temp_msg.delete()
    
        madflix_msgs = [] 
        for msg in messages:
            # Custom Caption Logic
            caption = CUSTOM_CAPTION.format(
                previouscaption="" if not msg.caption else msg.caption.html, 
                filename=msg.document.file_name if msg.document else "File"
            ) if bool(CUSTOM_CAPTION) and (msg.document or msg.video) else ("" if not msg.caption else msg.caption.html)
            
            reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(
                    chat_id=user_id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_CONTENT
                )
                madflix_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=user_id, caption=caption, reply_markup=reply_markup)
                madflix_msgs
                
