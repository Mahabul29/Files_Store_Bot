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
            text = f"<b>🤖 My Name :</b> <a href='https://t.me/Files_Store9_Bot'>File Sharing Bot</a>\n<b>📝 Language :</b> Python 3\n<b>📚 Library :</b> Pyrogram {__version__}\n<b>🚀 Server :</b> Koyeb\n<b>🧑‍💻 Developer :</b> <a href='tg://user?id={OWNER_ID}'>@Mahabul201</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔒 Close", callback_data = "close")]]
            )
        )
    
    # 2. Logic for resending files when "♻️ Get Files Again" is pressed
    elif data == "refresh_files":
        await query.answer("♻️ Fetching your files again...", show_alert=False)
        # This will trigger the start logic to resend the media
        from plugins.start import start_command
        await start_command(client, query.message)

    # 3. Logic for the "Close ✖️" button in the auto-delete notice
    elif data == "close_msg":
        await query.message.delete()

    # 4. Standard Close button logic
    elif data == "close":
        await query.message.delete()
        
