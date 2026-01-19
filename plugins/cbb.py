from pyrogram import __version__, filters
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Inside plugins/cbb.py

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    if data == "about":
        await query.message.edit_text(
            text = f"<b>Mʏ Nᴀᴍᴇ :</b> <a href='https://t.me/Files_Store9_Bot'>Nᴏᴛʜɪɴɢ</a>\n"
                   f"<b>Sᴇʀᴠᴇʀ :</b> <a href='https://app.koyeb.com/'>Kᴏʏᴇʙ</a>\n"
                   f"<b>Dᴇᴠᴇʟᴏᴘᴇʀ :</b> <a @Mahabul201'>Mᴏᴏɴ</a>\n"
                   f"<b>Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/EvaLinks'>Eᴠᴀ Lɪɴᴋs</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Bᴀᴄᴋ", callback_data="start"),
                        InlineKeyboardButton("Close ✖️", callback_data="close")
                    ]
                ]
            )
        )
    
    # FIX: Define the buttons here instead of using the undefined 'START_BUTTONS'
    elif data == "start":
        await query.message.edit_text(
            text = "<b>Main Menu</b>\n\nSelect an option below:",
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("About", callback_data="about"),
                        InlineKeyboardButton("Close", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "close":
        await query.message.delete()
        
