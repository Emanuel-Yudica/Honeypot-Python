from aiohttp import web
from datetime import datetime
import asyncio
async def handler(request):
    q = request.app["queue"]

    event = {
        "server": "HTTP",
        "time": datetime.now().isoformat(),
        "ip": request.remote,
        "method": request.method,
        "path": request.path,
        "query": dict(request.query),
        "headers": dict(request.headers),
        "user_agent": request.headers.get("User-Agent"),
    }

    q.put(event)
    return web.Response(status=200)

async def run_http_server(q):
    app = web.Application()
    app["queue"] = q
    app.router.add_route("*", "/{tail:.*}", handler)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 80)
    await site.start()

    print("[+] HTTP honeypot escuchando en 80")

    # mantiene vivo el loop
    while True:
        await asyncio.sleep(3600)
