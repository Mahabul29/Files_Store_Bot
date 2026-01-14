from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Bot is Running")

async def web_server():
    app = web.Application()
    app.add_routes(routes)
    return app
  
