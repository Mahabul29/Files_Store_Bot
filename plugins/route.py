import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DELETE_TIME # Make sure DELETE_TIME is defined in your config

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
# Inside the function where you send the file (usually hello_revive or similar)
async def send_media_and_handle_delete(client, message, file_id):
    # Send the actual file
    file_msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption="**Your file is ready! It will be deleted shortly.**"
    )

    # Background task to wait, delete, and show the RECALL BUTTON
    async def delete_after_delay():
        # Delay from config or default to 30 minutes (1800 seconds)
        await asyncio.sleep(int(DELETE_TIME) if DELETE_TIME else 1800)
        
        try:
            # Delete the media message
            await file_msg.delete()
            
            # SEND THE RECALL MESSAGE INSTEAD OF THE "SUCCESSFULLY DELETED" TEXT
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

    # Fire and forget the task so the bot stays responsive
    asyncio.create_task(delete_after_delay())
    
