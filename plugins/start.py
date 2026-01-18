import os, asyncio, humanize, time, requests
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

# --- CONFIGURATION ---
VERIFIED_USERS = {}  # Stores user_id: timestamp
VERIFY_EXPIRE = 10800  # 3 Hours in seconds
# Correct API format for Shortxlinks
SHORTENER_API = "https://shortxlinks.com/api?api=2392d1c0c3394bf02eb10ba9052123ab8&url={url}&format=json"
# ---------------------

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
        
        # --- LINK SHORTENER LOGIC ---
        user_id = message.from_user.id
        curr_time = time.time()
        
        # Check if user needs verification
        last_ver = VERIFIED_USERS.get(user_id, 0)
        
        if (curr_time - last_ver) > VERIFY_EXPIRE:
            # Check if they are returning from a shortener link
            if base64_string.startswith("verify_"):
                VERIFIED_USERS[user_id] = curr_time
                # Strip the verify_ prefix to get the real base64 data
                base64_string = base64_string.replace("verify_", "")
            else:
                # Generate the deep-link that the shortener will redirect back to
                verify_link = f"https://t.me/{client.username}?start=verify_{base64_string}"
                
                try:
                    r = requests.get(SHORTENER_API.format(url=verify_link), timeout=10)
                    data = r.json()
                    # Extract the shortened link
                    short_url = data.get("shortenedUrl", verify_link)
                except Exception as e:
                    print(f"Shortener API Error: {e}")
                    short_url = verify_link
                
                btn = [[InlineKeyboardButton("🔓 Unlock Files (3 Hours)", url=short_url)]]
                
                return await message.reply_text(
                    f"<b>Verify to Continue!</b>\n\nYour session has expired. Please verify via the link below to access files for the next 3 hours.",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
        # --- END LINK SHORTENER LOGIC ---

        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
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
            if bool(CUSTOM_CAPTION) and bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

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

        k = await client.send_message(chat_id=message.from_user.id, text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete}.\n\n📌 Please Forward This Video / File To Somewhere Else.")
        asyncio.create_task(delete_files(madflix_msgs, client, k))
        return
    else:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("👋 About Me", callback_data="about"), InlineKeyboardButton("🔒 Close", callback_data="close")]])
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
        return

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [[InlineKeyboardButton(text="Join Channel", url=client.invitelink)]]
    try:
        buttons.append([InlineKeyboardButton(text='Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    await message.reply_photo(
        photo="https://www.uhdpaper.com/2023/07/genshin-impact-furina-game-4k-161m.html",
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name or "",
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=False
    )

async def delete_files(messages, client, k):
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except:
            pass
    try:
        await k.edit_text("Your Video / File Is Successfully Deleted ✅")
    except:
        pass
        
