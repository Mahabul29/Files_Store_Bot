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
            TEXT = f"<b>Mʏ Nᴀᴍᴇ :</b> <a href='https://t.me/Files_Store9_Bot'>Nᴏᴛʜɪɴɢ</a>\n<b>Sᴇʀᴠᴇʀ :</b> Kᴏʏᴇʙ\n<b>Dᴇᴠᴇʟᴏᴘᴇʀ :</b> <a href='tg://user?id={OWNER_ID}'>@Mahabul201</a>\n<b>Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/EvaLinks'>Eᴠᴀ Lɪɴᴋs</a>"
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Cʟᴏsᴇ✖️", callback_data = "close")]]
            )
        )
    
    # 2. Logic for the "♻️ Get Files Again" button
    elif data == "refresh_files":
        await query.answer("♻️ Fetching your files again...", show_alert=False)
        # This deletes the "Message Was Deleted" notice and triggers the resend logic
        await query.message.delete()
        
        # Import inside the function to avoid circular import errors
        from plugins.start import start_command
        await start_command(client, query.message)

    # 3. Logic for the "Close ✖️" button in the auto-delete notice
    elif data == "close_msg":
        await query.message.delete()

    # 4. Standard Close button logic
    elif data == "close":
        await query.message.delete()
        
