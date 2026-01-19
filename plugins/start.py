import os, asyncio, humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)

# --- FIXED: Function now receives 'original_link' to update the button ---
async def delete_files(messages, client, k, original_link):
    await asyncio.sleep(jishudeveloper)
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass
    try:
        # This replaces the "Important" notice with the link button
        await k.edit_text(
            text="<b>Files Deleted! Click below to get them again.</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ", url=original_link)]]
            )
        )
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
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            ids = range(start,end+1) if start <= end else []
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
            caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document) else ("" if not msg.caption else msg.caption.html)
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except:
                pass

        # Capture the link for the "Previous Message" button
        current_link = f"https://t.me/{client.username}?start={base64_string}"

        k = await client.send_message(
            chat_id=message.from_user.id, 
            text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There."
        )

        asyncio.create_task(delete_files(madflix_msgs, client, k, current_link))
        return

    else:
        await message.reply_photo(
            photo="https://www.uhdpaper.com/2023/07/genshin-impact-furina-game-4k-161m.html", 
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👋 About Me", callback_data="about"), InlineKeyboardButton("🔒 Close", callback_data="close")]])
        )
        return

# --- BROADCAST SECTION ---
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=f"Processing...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} Users Are Using This Bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0
        pls_wait = await message.reply("<i>Broadcasting Message...</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
            total += 1
        status = f"<b><u>Broadcast Completed</u></b>\n\n<b>Total:</b> <code>{total}</code>\n<b>Success:</b> <code>{successful}</code>\n<b>Blocked:</b> <code>{blocked}</code>"
        return await pls_wait.edit(status)
    else:
        await message.reply(f"Reply to a message to broadcast it.")
        return
        
