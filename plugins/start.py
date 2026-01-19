import os, asyncio, humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)

# --- ADD THIS FUNCTION HERE TO PREVENT NameError ---
async def delete_files(messages, client, k):
    await asyncio.sleep(jishudeveloper)
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass
    try:
        await k.delete()
    except:
        pass

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        
        # ... [Logic for finding IDs remains same] ...
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something Went Wrong..!")
            return
        await temp_msg.delete()
    
        madflix_msgs = [] 

        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except:
                pass

        # This sends the "Important" notice seen in your screenshot
        k = await client.send_message(chat_id = message.from_user.id, text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.")

        # This will now work because the function is defined above
        asyncio.create_task(delete_files(madflix_msgs, client, k))
        return

    else:
        # --- FIX: THIS IS THE START MESSAGE WITH BUTTONS ---
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👋 About Me", callback_data = "about"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
        try:
            await message.reply_photo(
                photo="https://www.uhdpaper.com/2023/07/genshin-impact-furina-game-4k-161m.html", # CHANGED: Valid photo URL
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
        except Exception as e:
            # Fallback to text if photo still fails
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name or "",
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup
            )
        return
        
