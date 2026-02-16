from aiohttp import web
from datetime import datetime
import asyncio
import redis
r = redis.Redis(host="localhost", port=6379, db=0)
async def handler(request):
    
    ip = request.remote

    
    q = request.app["queue"]

    event = {
        "server": "HTTP",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "ip": request.remote,
        "method": request.method,
        "path": request.path,
        "query": dict(request.query),
        "headers": dict(request.headers),
        "user_agent": request.headers.get("User-Agent"),
    }

    q.put(event)
    # verificar si está bloqueada
    if r.exists(f"blocked:{ip}"):

        print(f"[BLOCKED] Intento de acceso de {ip}")

        return web.Response(
            status=403,
            text="Forbidden"
        )
    return web.Response(status=200)

async def run_http_server(q):
    app = web.Application()
    app["queue"] = q
    app.router.add_route("*", "/{tail:.*}", handler)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("[+] HTTP honeypot escuchando en 8080")

    # mantiene vivo el loop
    while True:
        await asyncio.sleep(3600)
