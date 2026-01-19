from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import START_MSG

@Bot.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    
        if data == "close":
        await query.message.delete()

    elif data == "about":
        # Ensure 'caption' is followed by a comma before 'reply_markup'
        caption = f"<b>Mʏ Nᴀᴍᴇ :</b> <a href='https://t.me/Files_Store9_Bot'><b>Nᴏᴛʜɪɴɢ</b></a>\n" \
                  f"<b>Sᴇʀᴠᴇʀ :</b> <a href='https://app.koyeb.com/'><b>Kᴏʏᴇʙ</b></a>\n" \
                  f"<b>Dᴇᴠᴇʟᴏᴘᴇʀ :</b> <a href='https://t.me/Mahabul201'><b>@Mᴀʜᴀʙᴜʟ201</b></a>\n" \
                  f"<b>Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/EvaLinks'><b>Eᴠᴀ Lɪɴᴋs</b></a>"
        
        await query.message.edit_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Bᴀᴄᴋ", callback_data="back_to_start"),
                 InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]
            ])
        )
        
    
    elif data == "back_to_start":
        # This handles the 'Go Back' action correctly
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
        
