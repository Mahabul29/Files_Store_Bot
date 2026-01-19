import os, asyncio, humanize, time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import (
    START_MSG, CUSTOM_CAPTION, PROTECT_CONTENT, 
    FILE_AUTO_DELETE, DISABLE_CHANNEL_BUTTON
)
from helper_func import subscribed, decode, get_messages
from database.database import add_user, present_user

# IMPORT: Make sure this matches your route.py button name
from plugins.route import RECALL_BUTTON

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try: await add_user(id)
        except: pass
    
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
            
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1)
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            else: return
        except: return

        temp_msg = await message.reply("Pʟᴇᴀsᴇ Wᴀɪᴛ...")
        try:
            messages = await get_messages(client, ids)
        except:
            return await message.reply_text("Something Went Wrong..!")
        
        await temp_msg.delete()
        madflix_msgs = []

        for msg in messages:
            caption = CUSTOM_CAPTION.format(
                previouscaption="" if not msg.caption else msg.caption.html, 
                filename=msg.document.file_name if msg.document else "File"
            ) if bool(CUSTOM_CAPTION) else ("" if not msg.caption else msg.caption.html)

            try:
                madflix_msg = await msg.copy(
                    chat_id=message.from_user.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=msg.reply_markup if DISABLE_CHANNEL_BUTTON else None, 
                    protect_content=PROTECT_CONTENT
                )
                madflix_msgs.append(madflix_msg)
                await asyncio.sleep(0.5) # Prevent flood waits
            except: pass

        # Notification message with the timer info
        file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)
        k = await client.send_message(
            chat_id=message.from_user.id, 
            text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nYᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {file_auto_delete}."
        )

        # Triggers the background delete task
        asyncio.create_task(delete_files(madflix_msgs, client, k))
    else:
        # Normal start message
        await message.reply_text(START_MSG)

async def delete_files(messages, client, k):
    """Wait, delete files, and then show the RECALL_BUTTON"""
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try: await client.delete_messages(msg.chat.id, msg.id)
        except: pass
    
    try:
        # Edits the warning message to the final "Deleted" state with the button
        await k.edit_text(
            text="**Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ Wᴀs Dᴇʟᴇᴛᴇᴅ** 🗑️\n\nClick below to get them again:",
            reply_markup=RECALL_BUTTON
        )
    except: pass
        
