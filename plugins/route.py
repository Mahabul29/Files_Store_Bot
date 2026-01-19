import asyncio
import humanize
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import FILE_AUTO_DELETE, CUSTOM_CAPTION, PROTECT_CONTENT, DISABLE_CHANNEL_BUTTON
from helper_func import get_messages

async def send_media_and_handle_delete(client, message, decoded_string, base64_string):
    # Parse IDs from decoded string
    argument = decoded_string.split("-")
    if len(argument) == 3:
        start = int(int(argument[1]) / abs(client.db_channel.id))
        end = int(int(argument[2]) / abs(client.db_channel.id))
        ids = range(start, end + 1)
    elif len(argument) == 2:
        ids = [int(int(argument[1]) / abs(client.db_channel.id))]
    else:
        return

    # Fetch and send messages
    temp_msg = await message.reply("Pʟᴇᴀsᴇ Wᴀɪᴛ...")
    messages = await get_messages(client, ids)
    await temp_msg.delete()

    sent_messages = []
    for msg in messages:
        caption = CUSTOM_CAPTION.format(
            previouscaption="" if not msg.caption else msg.caption.html, 
            filename=msg.document.file_name if msg.document else "File"
        ) if bool(CUSTOM_CAPTION) else ("" if not msg.caption else msg.caption.html)

        m = await msg.copy(
            chat_id=message.from_user.id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            protect_content=PROTECT_CONTENT,
            reply_markup=msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
        )
        sent_messages.append(m)
        await asyncio.sleep(0.5)

    # Create the "Get Again" button
    share_link = f"https://t.me/{client.me.username}?start={base64_string}"
    recall_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("Get Files Again 🔄", url=share_link)
    ]])

    # Send Warning
    time_text = humanize.naturaldelta(FILE_AUTO_DELETE)
    warn_msg = await client.send_message(
        chat_id=message.from_user.id,
        text=f"<b>❗️ IMPORTANT ❗️</b>\n\nYour files will be deleted in {time_text}.",
        reply_markup=recall_markup
    )

    # Start the delete timer
    asyncio.create_task(delete_task(sent_messages, client, warn_msg, recall_markup))

async def delete_task(messages, client, warn_msg, recall_markup):
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try: await client.delete_messages(msg.chat.id, msg.id)
        except: pass
    
    try:
        await warn_msg.edit_text(
            "**Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇs Wᴇʀᴇ Dᴇʟᴇᴛᴇᴅ** 🗑️\n\nClick below to get them again:",
            reply_markup=recall_markup
        )
    except: pass
        
