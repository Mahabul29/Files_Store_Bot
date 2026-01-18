from aiohttp import web
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton # Add this import

routes = web.RouteTableDef()

# --- ADD THIS HERE ---
RECALL_BUTTON = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Click Here", callback_data="refresh_files"),
        InlineKeyboardButton("Close ✖️", callback_data="close_msg")
    ]
])
# ---------------------

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Madflix_Bots")
    
