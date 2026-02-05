from aiohttp import web
from datetime import datetime

async def handle(request):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    event = {
        "time": now,
        "ip": request.remote,
        "method": request.method,
        "path": request.path,
        "query": dict(request.query),
        "headers": dict(request.headers),
        "user_agent": request.headers.get("User-Agent"),
    }

    print(event)

   
    return web.Response(status=200, text="")
app = web.Application()
app.router.add_route("*", "/{tail:.*}", handle)

web.run_app(app, port=80)
