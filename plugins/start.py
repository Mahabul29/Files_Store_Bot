import os, asyncio, humanize, time, requests
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE
)
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

# Import the button logic from route.py
from plugins.route import RECALL_BUTTON

madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            ids = range(start, end + 1) if start <= end else []
            if start > end:
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end: break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        else:
            return

        temp_msg = await message.reply("Pʟᴇᴀsᴇ Wᴀɪᴛ...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something Went Wrong..!")
            return
        await temp_msg.delete()
    
        madflix_msgs = []
        for msg in messages:
            caption = CUSTOM_CAPTION.format(
                previouscaption="" if not msg.caption else msg.caption.html, 
                filename=msg.document.file_name
            ) if bool(CUSTOM_CAPTION) and bool(msg.document) else ("" if not msg.caption else msg.caption.html)

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                madflix_msg = await msg.copy(
                    chat_id=message.from_user.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_CONTENT
                )
                madflix_msgs.append(madflix_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(
                    chat_id=message.from_user.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_CONTENT
                )
                madflix_msgs.append(madflix_msg)
            except:
                pass

        # Send the "Important" notification message
        k = await client.send_message(
            chat_id=message.from_user.id, 
            text=(
                "<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\n"
                "⚠️ **Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....**\n\n"
                f"Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {file_auto_delete}. "
                "Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.\n\n"
                "**ɴᴏᴛᴇ :** ᴜsᴇ ᴠʟᴄ ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ ɢᴏᴏᴅ ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ ᴀᴘᴘ ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ!"
            )
        )

        # Start the background deletion task
        asyncio.create_task(delete_files(madflix_msgs, client, k))
        return

    else:
        # Standard Start Message
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Aʙᴏᴜᴛ ᴍᴇ", callback_data="about"), 
             InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")]
        ])
        await message.reply_photo(
            photo="https://www.uhdpaper.com/2023/07/genshin-impact-furina-game-4k-161m.html",
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            quote=False
        )

# Other handlers (not_joined, get_users, send_text) remain unchanged...

async def delete_files(messages, client, k):
    """Handles file deletion and updates the notification with the recall button."""
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"Error deleting media {msg.id}: {e}")
    
    # Update notification to show the Recall Button
        try:
        await k.edit_text(
            text=(
                "**Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ Wᴀs Dᴇʟᴇᴛᴇᴅ** 🗑️\n\n"
                "If you want to get the files again, then click: "
                "[⭕ Click Here] button below else close this message."
            ),
            reply_markup=RECALL_BUTTON
        )
    except Exception as e:
        print(f"Error updating deletion message: {e}")
    
