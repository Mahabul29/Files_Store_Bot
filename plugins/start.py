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

# Note: We are now creating the button dynamically based on the file link
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
                await asyncio.sleep(0.5) 
            except: pass

        # --- DYNAMIC BUTTON LOGIC ---
        file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)
        
        # This creates the unique "Get Again" link for these specific files
        share_link = f"https://t.me/{client.me.username}?start={base64_string}"
        
        recall_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Get Files Again 🔄", url=share_link)]
        ])

        # Sending the Warning Message
        k = await client.send_message(
            chat_id=message.from_user.id, 
            text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nYᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {file_auto_delete}.",
            reply_markup=recall_markup
        )

        # Triggers the background delete task and passes the button markup
        asyncio.create_task(delete_files(madflix_msgs, client, k, recall_markup))
    else:
        # Normal start message
        await message.reply_text(START_MSG)

async def delete_files(messages, client, k, recall_markup):
    """Wait, delete files, and then show the RECALL button"""
    await asyncio.sleep(FILE_AUTO_DELETE)
    
    # Delete the actual file messages
    for msg in messages:
        try: await client.delete_messages(msg.chat.id, msg.id)
        except: pass
    
    try:
        # Edit the warning message to show files are gone, but keep the link
        await k.edit_text(
            text="**Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇs Wᴇʀᴇ Dᴇʟᴇᴛᴇᴅ** 🗑️\n\nClick the button below to get them again:",
            reply_markup=recall_markup
        )
    except: pass
        
