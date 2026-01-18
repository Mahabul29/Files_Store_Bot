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

# --- CONFIGURATION ---
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    """Handles the start command and delivers files directly."""
    user_id = message.from_user.id
    
    # Add user to database if they are new
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

        temp_msg = await message.reply("<b>🔎 Searching for your files...</b>")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("<b>❌ Error:</b> Files not found in the database.")
            return
        await temp_msg.delete()
    
        delivered_msgs = [] 
        for msg in messages:
            # Set up the caption
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
                delivered_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=user_id, caption=caption, reply_markup=reply_markup)
                delivered_msgs.append(copied_msg)
            except:
                pass

        # Deletion Alert
        k = await client.send_message(
            chat_id=user_id, 
            text=f"<b>🚀 Files Delivered!</b>\n\n<b>Note:</b> To save storage, these files will be deleted in <b>{file_auto_delete}</b>."
        )
        # Start the deletion timer
        asyncio.create_task(delete_files(delivered_msgs, client, k))
        return
    else:
        # Normal Start (No file link)
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✨ Support Group", url="https://t.me/your_group")]])
        )

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    """Shows the join channel requirement."""
    buttons = [[InlineKeyboardButton(text="📢 Join Channel", url=client.invitelink)]]
    try:
        # Redirect back to the file they wanted after joining
        buttons.append([InlineKeyboardButton(text='🔄 Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except:
        pass
        
    await message.reply_photo(
        photo=START_PIC,
        caption=FORCE_MSG.format(first=message.from_user.first_name, mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def delete_files(messages, client, k):
    """Timer logic to delete messages automatically."""
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except: 
            pass
    try:
        await k.edit_text("<b>⚠️ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....n\n\Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 30 Mɪɴᴜᴛᴇs. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.\n\nɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ ɢᴏᴏᴅ ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ ᴀᴘᴘ ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ!</b>")
    except: 
        pass
        
