from pyrogram import __version__, filters
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Inside plugins/cbb.py

@Bot.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    
    if data == "close":
        await query.message.delete()
        
    elif data == "about":
        # This edits the message to show "About" info and the new Back button
        await query.message.edit_caption(
            caption=f"<b>Mʏ Nᴀᴍᴇ :</b> <a href='https://t.me/Files_Store9_Bot'>Nᴏᴛʜɪɴɢ</a>\n"
                    f"<b>Sᴇʀᴠᴇʀ :</b> <a href='https://app.koyeb.com/'>Kᴏʏᴇʙ</a>\n"
                    f"<b>Dᴇᴠᴇʟᴏᴘᴇʀ :</b> <a href='https://t.me/Mahabul201'>Mᴏᴏɴ</a>\n"
                    f"<b>Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/EvaLinks'>Eᴠᴀ Lɪɴᴋs</a>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Bᴀᴄᴋ", callback_data="back_to_start"),
                    InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")
                ]
            ])
        )

    elif data == "back_to_start":
        # This restores the original message exactly as it appears in start.py
        await query.message.edit_caption(
            caption=START_MSG.format(
                first=query.from_user.first_name,
                last=query.from_user.last_name or "",
                mention=query.from_user.mention,
                id=query.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Aʙᴏᴜᴛ Mᴇ", callback_data="about"), 
                    InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")
                ]
            ])
        )
        
