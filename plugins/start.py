import os
import asyncio
import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE, 
    START_PIC, FORCE_PIC, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL_2
)
from helper_func import encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

# Global Variables
madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)

# --- 1. AUTO DELETE LOGIC ---
async def delete_files(messages, client, k, original_link):
    await asyncio.sleep(jishudeveloper)
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass
    try:
        await k.edit_text(
            text="<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ Wᴀs Dᴇʟᴇᴛᴇᴅ...</b>\n\n"
                 "<blockquote><b>Iғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: "
                 "[Cʟɪᴄᴋ Hᴇʀᴇ] ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Cʟɪᴄᴋ Hᴇʀᴇ", url=original_link),
                 InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]
            ])
        )
    except:
        pass

# --- 2. START COMMAND HANDLER ---
@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    
    # MULTI-FORCE SUBSCRIBE LOGIC
    buttons = []
    join_row = [] 
    
    if FORCE_SUB_CHANNEL:
        try:
            await client.get_chat_member(FORCE_SUB_CHANNEL, id)
        except UserNotParticipant:
            chat = await client.get_chat(FORCE_SUB_CHANNEL)
            join_row.append(InlineKeyboardButton("Jᴏɪɴ Cʜᴀɴɴᴇʟ 1", url=chat.invite_link))
        except Exception: pass

    if FORCE_SUB_CHANNEL_2:
        try:
            await client.get_chat_member(FORCE_SUB_CHANNEL_2, id)
        except UserNotParticipant:
            chat = await client.get_chat(FORCE_SUB_CHANNEL_2)
            join_row.append(InlineKeyboardButton("Jᴏɪɴ Cʜᴀɴɴᴇʟ 2", url=chat.invite_link))
        except Exception: pass

    if join_row:
        buttons.append(join_row)

    if buttons:
        if len(message.command) > 1:
            buttons.append([InlineKeyboardButton(text='Tʀʏ Aɢᴀɪɴ', url=f"https://t.me/{client.username}?start={message.command[1]}")])
        
        return await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                mention=message.from_user.mention,
                id=id
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # DATABASE REGISTRATION
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
            
    # FILE RETRIEVAL LOGIC
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
            caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document) else ("" if not msg.caption else msg.caption.html)
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                madflix_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except:
                pass

        current_link = f"https://t.me/{client.username}?start={base64_string}"
        
        k = await client.send_message(
            chat_id=id, 
            text=f"<b>❗️ <u>Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....</u></b>\n\n"
                 f"<blockquote><b>Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {file_auto_delete}. "
                 f"Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.</b></blockquote>"
        )
        
        asyncio.create_task(delete_files(madflix_msgs, client, k, current_link))
        return

    # NORMAL START MENU (NEW UI)
    else:
        buttons = [
            [
                InlineKeyboardButton("• ABOUT •", callback_data="about"), 
                InlineKeyboardButton("• HELP •", callback_data="help")
            ],
            [
                InlineKeyboardButton("SETTINGS", callback_data="settings")
            ]
        ]
        
        start_caption = (
            f"Hello {message.from_user.mention} ~\n\n"
            "<blockquote><b>I AM A ADVANCE LINK SHARE BOT THROUGH WHICH "
            "YOU CAN GET THE LINKS OF SPECIFIC CHANNELS WHICH SAVE "
            "YOUR CHANNELS FROM COPYRIGHT.</b></blockquote>"
        )

        await message.reply_photo(
            photo=START_PIC, 
            caption=start_caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# --- 3. CALLBACK HANDLERS ---
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "settings":
        if query.from_user.id not in ADMINS:
            return await query.answer("Access Denied!", show_alert=True)
        
        settings_text = (
            "<b>⚙️ Bᴏᴛ Sᴇᴛᴛɪɴɢs</b>\n\n"
            f"• Aᴜᴛᴏ Dᴇʟᴇᴛᴇ: <code>{file_auto_delete}</code>\n"
            f"• Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ: <code>{'ON' if PROTECT_CONTENT else 'OFF'}</code>\n"
            f"• Cᴜsᴛᴏᴍ Cᴀᴘᴛɪᴏɴ: <code>{'ON' if CUSTOM_CAPTION else 'OFF'}</code>"
        )
        await query.message.edit_text(settings_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back")]]))

    elif data == "about":
        await query.message.edit_text("<b>Aʙᴏᴜᴛ Mᴇ:</b>\nI save your channels from copyright!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back")]]))

    elif data == "help":
        await query.message.edit_text("<b>Hᴇʟᴘ:</b>\nSend links or files to the bot.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back")]]))

    elif data == "back":
        # Since the original was a photo, we edit the caption or send a new start message
        await query.message.delete()
        # Call the start logic again or manually send the photo
        buttons = [[InlineKeyboardButton("• ABOUT •", callback_data="about"), InlineKeyboardButton("• HELP •", callback_data="help")], [InlineKeyboardButton("SETTINGS", callback_data="settings")]]
        await client.send_photo(chat_id=query.from_user.id, photo=START_PIC, caption=f"Hello {query.from_user.mention} ~\n\n<blockquote><b>I AM A ADVANCE LINK SHARE BOT...</b></blockquote>", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "close":
        await query.message.delete()

# --- 4. BROADCAST COMMAND ---
@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast!")
    
    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0
    pls_wait = await message.reply("📢 Broadcasting...")
    
    for chat_id in query:
        try:
            await broadcast_msg.copy(chat_id)
            successful += 1
        except UserIsBlocked:
            await del_user(chat_id); blocked += 1
        except Exception:
            unsuccessful += 1
        total += 1

    await pls_wait.edit(f"Total: {total} | Success: {successful} | Failed: {unsuccessful}")
    
