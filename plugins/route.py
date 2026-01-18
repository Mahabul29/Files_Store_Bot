import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
[span_0](start_span)from config import DELETE_TIME  #[span_0](end_span)

# --- 1. DEFINE THE BUTTONS ---
RECALL_BUTTON = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⭕ Click Here", callback_data="refresh_files"),
        InlineKeyboardButton("Close ✖️", callback_data="close_msg")
    ]
])

# --- 2. WEB SERVER ROUTES ---
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Madflix_Bots")

# --- 3. AUTO-DELETE & RECALL LOGIC ---
async def send_media_and_handle_delete(client, message, file_id):
    """Sends media and starts the background auto-delete timer."""
    # Send the actual file
    file_msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption="**Your file is ready! It will be deleted shortly for security.**"
    )

    async def delete_after_delay():
        # [span_1](start_span)Delay from config[span_1](end_span) or default to 1800 seconds
        await asyncio.sleep(int(DELETE_TIME) if DELETE_TIME else 1800)
        
        try:
            # Delete the media message
            await file_msg.delete()
            
            # Send the recall notification with the button
            await client.send_message(
                chat_id=message.from_user.id,
                text=(
                    "**Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ Wᴀs Dᴇʟᴇᴛᴇᴅ** 🗑️\n\n"
                    "If you want to get the files again, then click: "
                    "[⭕ Click Here] button below else close this message."
                ),
                reply_markup=RECALL_BUTTON
            )
        except Exception as e:
            print(f"Error in deletion task: {e}")

    # Start background task
    asyncio.create_task(delete_after_delay())

# --- 4. NEW CODE: THE HANDLER ---
# This part connects the bot's start command to your deletion logic
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    # Check if the start command has a file ID (e.g., /start file_id_123)
    if len(message.command) > 1:
        file_id = message.command[1]
        
        # This calls your auto-delete function automatically
        await send_media_and_handle_delete(client, message, file_id)
    else:
        await message.reply_text("Send me a valid file link to get started!")
        
