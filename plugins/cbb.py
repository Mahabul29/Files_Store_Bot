from pyrogram import __version__, filters
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    # 1. Logic for the "About Me" button
    if data == "about":
        await query.message.edit_text(
            text = f"<b>Mʏ Nᴀᴍᴇ :</b> <a href='https://t.me/Files_Store9_Bot'>Nᴏᴛʜɪɴɢ</a>\n"
                   f"<b>Sᴇʀᴠᴇʀ :</b> <a href='https://app.koyeb.com/'>Kᴏʏᴇʙ</a>\n"
                   f"<b>Dᴇᴠᴇʟᴏᴘᴇʀ :</b> <a href='tg://user?id={OWNER_ID}'>Moon</a>\n"
                   f"<b>Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/EvaLinks'>Eᴠᴀ Lɪɴᴋs</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Cʟᴏsᴇ✖️", callback_data = "close")]]
            )
        )
        
