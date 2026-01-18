import os, asyncio, humanize, time, requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE,
    SHORTENER_API, START_PIC
)
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, present_user

# --- SETUP ---
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# --- MANUAL SHORTENER COMMAND ---
@Bot.on_message(filters.command('shortener') & filters.private)
async def manual_shortener(client: Client, message: Message):
    """Command to manually shorten a URL using the API from Environment Variables."""
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b>\n<code>/shortener https://yourlink.com</code>")
    
    url = message.text.split(None, 1)[1]
    msg = await message.reply("<code>Generating Short Link...</code>")
    
    try:
        # Construct API call using the SHORTENER_API from your config
        api_url = f"{SHORTENER_API}&url={url}"
        r = requests.get(api_url, timeout=10)
        data = r.json()
        
        # Look for the shortened URL in the response
        short_url = data.get("shortened_url") or data.get("url") or data.get("short_url")
        
        if short_url:
            btn = [[InlineKeyboardButton("🔗 Open Short Link", url=short_url)]]
            await msg.edit_text(
                f"<b>✅ Link Shortened!</b>\n\n<b>Original:</b> {url}\n<b>Shortened:</b> {short_url}",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True
            )
        else:
            await msg.edit_text("<b>❌ Error:</b> Could not retrieve short link from API. Check your API key.")
            
    except Exception as e:
        await msg.edit_text(f"<b>❌ API Error:</b> {str(e)}")

# --- START COMMAND (DIRECT FILE DELIVERY) ---
@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    """The Start command now provides files directly without link shortener redirection."""
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
        
        # --- DIRECT FILE DELIVERY LOGIC ---
        # This part decodes the link and sends files immediately
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

        temp_msg = await message.reply("<b>Sending your files, please wait...</b>")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong while fetching files.")
            return
        await temp_msg.delete()
    
        madflix_msgs = [] 
        for msg in messages:
            # Apply custom caption if set
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
                madflix_msgs.append(copied_msg)
            except:
                pass

        # Send deletion notification
        k = await client.send_message(
            chat_id=user_id, 
            text=f"<b>❗️ IMPORTANT ❗️</b>\n\nYour files will be automatically deleted in {file_auto_delete}."
        )
        # Start the auto-delete timer
        asyncio.create_task(delete_files(madflix_msgs, client, k))
        return
    else:
        # Standard Welcome Message with START_PIC from Environment Variables
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👋 About Me", callback_data="about")]])
        )

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    """Force Subscription message using START_PIC."""
    buttons = [[InlineKeyboardButton(text="Join Channel", url=client.invitelink)]]
    try:
        # Add 'Try Again' button if they were trying to access a file
        buttons.append([InlineKeyboardButton(text='Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except:
        pass
        
    await message.reply_photo(
        photo=START_PIC,
        caption=FORCE_MSG.format(first=message.from_user.first_name, mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def delete_files(messages, client, k):
    """Logic to delete files after the set time in Environment Variables."""
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except: 
            pass
    try:
        await k.edit_text("<b>Your files have been successfully deleted ✅</b>")
    except: 
        pass
        
