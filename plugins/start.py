import os, asyncio, humanize, time, requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# Use a direct link to an image (must end in .jpg, .png, etc.)
START_PIC = "https://graph.org/file/e322f254928e08d506725.jpg"

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    
    # 1. Add user to database
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    # 2. Check Force Subscribe
    if not await subscribed(client, message):
        buttons = [[InlineKeyboardButton("Join Channel", url=client.invitelink)]]
        if len(message.command) > 1:
            buttons.append([InlineKeyboardButton("Try Again", url=f"https://t.me/{client.username}?start={message.command[1]}")])
        
        return await message.reply_photo(
            photo=START_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # 3. Handle File Links (if any)
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
            
            # Logic to get file IDs
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1)
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            else:
                return

            temp_msg = await message.reply("Processing your files...")
            messages = await get_messages(client, ids)
            await temp_msg.delete()
            
            sent_msgs = []
            for msg in messages:
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name) if CUSTOM_CAPTION and msg.document else (msg.caption.html if msg.caption else "")
                reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
                
                try:
                    s_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    sent_msgs.append(s_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    s_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    sent_msgs.append(s_msg)

            k = await client.send_message(chat_id=id, text=f"<b>❗️ IMPORTANT ❗️</b>\n\nYour files will be deleted in {file_auto_delete} due to copyright issues.")
            asyncio.create_task(delete_files(sent_msgs, client, k))
            return
            
        except Exception as e:
            print(f"Error in start link: {e}")
            return

    # 4. Default Start Message
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("Aʙᴏᴜᴛ ᴍᴇ", callback_data="about"),
        InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")
    ]])
    
    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name or "",
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup
    )

async def delete_files(messages, client, k):
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except:
            pass
    await k.edit_text("<b>Yᴏᴜʀ Vɪᴅᴇᴏ / Fɪʟᴇ Is Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ ✅</b>")
