import os, asyncio, humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE, 
    START_PIC, FORCE_PIC, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL_2
)
from helper_func import encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

# Humanized delete time for display
auto_delete_time = humanize.naturaldelta(FILE_AUTO_DELETE)

async def delete_files(messages, client, k, original_link):
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass
    try:
        # Auto-delete message with Quote Design
        await k.edit_text(
            text="<blockquote expandable><b>🗑️ Fɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs!\n\n"
                 "🔄 Wᴀɴᴛ ᴛʜᴇᴍ ʙᴀᴄᴋ? Jᴜsᴛ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.</b></blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Cʟɪᴄᴋ Hᴇʀᴇ", url=original_link),
                 InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]
            ]),
            disable_web_page_preview=True
        )
    except:
        pass

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    
    # --- 1. MULTI-FORCE SUBSCRIBE LOGIC ---
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
            buttons.append([InlineKeyboardButton(text='🔄 Tʀʏ Aɢᴀɪɴ', url=f"https://t.me/{client.username}?start={message.command[1]}")])
        
        # Force Sub Message with Quote Design
        await message.reply_photo(
            photo=FORCE_PIC,
            caption=f"<blockquote expandable>{FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or '',
                mention=message.from_user.mention,
                id=id
            )}</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # --- 2. DATABASE ---
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
            
    # --- 3. FILE RETRIEVAL ---
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
            else:
                return

            temp_msg = await message.reply("<blockquote><b>Pʟᴇᴀsᴇ Wᴀɪᴛ... ⌛</b></blockquote>", parse_mode=ParseMode.HTML)
            messages = await get_messages(client, ids)
            await temp_msg.delete()
    
            sent_msgs = [] 
            for msg in messages:
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document) else ("" if not msg.caption else msg.caption.html)
                reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

                try:
                    sent_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    sent_msgs.append(sent_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    sent_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    sent_msgs.append(sent_msg)
                except:
                    pass

            current_link = f"https://t.me/{client.username}?start={base64_string}"
            
            # File Expiry Notification with Quote Design
            k = await client.send_message(
                chat_id=id, 
                text=f"<b>❗️ <u>Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....</u></b>\n\n"
                     f"<blockquote expandable><b>Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {auto_delete_time}.\n\n"
                     f"Pʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ/sᴀᴠᴇ ᴛʜᴇᴍ ᴇʟsᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴛʜᴇʏ ᴠᴀɴɪsʜ!</b></blockquote>",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            asyncio.create_task(delete_files(sent_msgs, client, k, current_link))
            return
        except Exception as e:
            await message.reply_text(f"<blockquote><b>Eʀʀᴏʀ:</b> {e}</blockquote>", parse_mode=ParseMode.HTML)
            return

    # --- 4. NORMAL START MESSAGE ---
    else:
        await message.reply_photo(
            photo=START_PIC, 
            caption=f"<blockquote expandable>{START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or '',
                mention=message.from_user.mention,
                id=id
            )}</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Aʙᴏᴜᴛ Mᴇ", callback_data="about"), 
                 InlineKeyboardButton("✖️ Cʟᴏsᴇ", callback_data="close")]
            ])
        )
        return
        
