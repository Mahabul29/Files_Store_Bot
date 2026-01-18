import os, asyncio, humanize, time, requests
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE,
    SHORTENER_API, SHORTENER_URL, START_PIC
)
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, present_user

# --- CONFIGURATION ---
VERIFIED_USERS = {}  
VERIFY_EXPIRE = 10800  
# ---------------------

file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

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
        
        # --- LINK SHORTENER LOGIC ---
        user_id = message.from_user.id
        curr_time = time.time()
        last_ver = VERIFIED_USERS.get(user_id, 0)
        
        if (curr_time - last_ver) > VERIFY_EXPIRE:
            if base64_string.startswith("verify_"):
                VERIFIED_USERS[user_id] = curr_time
                base64_string = base64_string.replace("verify_", "")
            else:
                verify_link = f"https://t.me/{client.username}?start=verify_{base64_string}"
                try:
                    api_url = f"{SHORTENER_API}&url={verify_link}"
                    r = requests.get(api_url, timeout=10)
                    data = r.json()
                    short_url = data.get("shortened_url") or data.get("url")
                    if not short_url:
                        return await message.reply_text("<b>Error:</b> Shortener API failed. Try again.")
                except Exception as e:
                    return await message.reply_text("<b>Shortener Service is down.</b>")
                
                btn = [[InlineKeyboardButton("🔓 Unlock Files (3 Hours)", url=short_url)]]
                return await message.reply_text(
                    f"<b>Verify to Continue!</b>\n\nYour session has expired. Please verify to access files.",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
        # --- END LINK SHORTENER LOGIC ---

        # --- FILE DELIVERY LOGIC ---
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

        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something Went Wrong..!")
            return
        await temp_msg.delete()
    
        madflix_msgs = [] 
        for msg in messages:
            caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document) else ("" if not msg.caption else msg.caption.html)
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(copied_msg)
            except:
                pass

        k = await client.send_message(chat_id=message.from_user.id, text=f"<b>❗️ IMPORTANT ❗️</b>\n\nFile will be deleted in {file_auto_delete}.")
        asyncio.create_task(delete_files(madflix_msgs, client, k))
        return
    else:
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(first=message.from_user.first_name, mention=message.from_user.mention, id=message.from_user.id),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👋 About Me", callback_data="about")]])
        )

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [[InlineKeyboardButton(text="Join Channel", url=client.invitelink)]]
    try:
        buttons.append([InlineKeyboardButton(text='Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except:
        pass
    await message.reply_photo(
        photo=START_PIC,
        caption=FORCE_MSG.format(first=message.from_user.first_name, mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def delete_files(messages, client, k):
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except: pass
    try:
        await k.edit_text("<b>Your Video / File Is Successfully Deleted ✅</b>")
    except: pass
            
