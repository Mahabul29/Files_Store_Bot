import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import DELETE_TIME

# --- 1. DEFINE THE BUTTONS ---
# FIXED: Changed 'InlineKeyboardWarkup' to 'InlineKeyboardMarkup'
RECALL_BUTTON = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("♻️ Get Files Again", callback_data="refresh_files"),
        InlineKeyboardButton("Close ✖️", callback_data="close_msg")
    ]
])

# --- 2. WEB SERVER ROUTES ---
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Madflix_Bots")

# --- 3. AUTO-DELETE LOGIC ---
async def send_media_and_handle_delete(client, message, file_id):
    try:
        # FIXED: Added error handling for the 'Failed to decode' issue in logs
        file_msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption="**Your file is ready! It will be deleted shortly for security.**"
        )
    except Exception as e:
        print(f"File ID Decode Error: {e}")
        return await message.reply_text("❌ Error: This file link is invalid or expired.")

    async def delete_after_delay():
        await asyncio.sleep(int(DELETE_TIME) if DELETE_TIME else 1800)
        try:
            await file_msg.delete()
            await client.send_message(
                chat_id=message.from_user.id,
                text="**Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ Wᴀs Dᴇʟᴇᴛᴇᴅ** 🗑️\n\nClick below to get it again:",
                reply_markup=RECALL_BUTTON
            )
        except Exception as e:
            print(f"Deletion error: {e}")

    asyncio.create_task(delete_after_delay())

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    # FIXED: This ensures the bot only tries to send media when a file ID is present
    if len(message.command) >
    
