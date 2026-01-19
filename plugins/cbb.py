from pyrogram import __version__, filters
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    if data == "about":
        await query.message.edit_text(
            text = f"<b>Mʏ Nᴀᴍᴇ :</b> <a href='https://t.me/Files_Store9_Bot'>Nᴏᴛʜɪɴɢ</a>\n"
                   f"<b>Sᴇʀᴠᴇʀ :</b> <a href='https://app.koyeb.com/'>Kᴏʏᴇʙ</a>\n"
                   f"<b>Dᴇᴠᴇʟᴏᴘᴇʀ :</b> <a href='tg://user?id={OWNER_ID}'>Moon</a>\n"
                   f"<b>Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/EvaLinks'>Eᴠᴀ Lɪɴᴋs</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔙 Go Back", callback_data="start"),
                        InlineKeyboardButton("Close ✖️", callback_data="close")
                    ]
                ]
            )
        )
    
    # IMPORTANT: You must have this block so the "Back" button works!
    elif data == "start":
        await query.message.edit_text(
            text = "Welcome back to the Main Menu!", # Change this to your start message
            reply_markup = START_BUTTONS # Ensure START_BUTTONS is defined
        )

    elif data == "close":
        await query.message.delete()
        
