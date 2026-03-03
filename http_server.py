
import os
from aiohttp import web
from datetime import datetime
import asyncio
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
async def handler(request):
    

    
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
  

     
    return web.Response(status=200)

async def run_http_server(q):
    app = web.Application()
    app["queue"] = q
    app.router.add_route("*", "/{tail:.*}", handler)

    runner = web.AppRunner(app)
    await runner.setup()

    HTTP_PORT = int(os.getenv("HTTP_PORT", 8080))

    site_v4 = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
    site_v6 = web.TCPSite(runner, "::", HTTP_PORT)
    
    # Arrancamos ambos de forma independiente dentro del mismo loop
    try:
        await site_v4.start()
        print(f"[+] HTTP escuchando en IPv4 (0.0.0.0:{HTTP_PORT})")
    except Exception as e:
        print(f"[!] Fallo IPv4: {e}")

    try:
        await site_v6.start()
        print(f"[+] HTTP escuchando en IPv6 ([::]:{HTTP_PORT})")
    except Exception as e:
        print(f"[!] Fallo IPv6: {e}")

    # Mantenemos la corrutina activa
    await asyncio.Event().wait()