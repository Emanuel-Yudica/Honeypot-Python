import os
from aiohttp import web
from datetime import datetime
import asyncio
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
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
    if r.exists(f"blocked:{ip}"):

    # solo loguea una vez por servicio
        if r.setnx(f"blocked_logged:http:{ip}", 1):

            print(f"[BLOCKED HTTP] {ip}")

            # expira igual que el bloqueo (10 min)
            r.expire(f"blocked_logged:http:{ip}", 600)

        return web.Response(
            status=403,
            text="Forbidden"
        )

    return web.Response(status=200)

import os
from aiohttp import web
from datetime import datetime
import asyncio
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
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
    if r.exists(f"blocked:{ip}"):

    # solo loguea una vez por servicio
        if r.setnx(f"blocked_logged:http:{ip}", 1):

            print(f"[BLOCKED HTTP] {ip}")

            # expira igual que el bloqueo (10 min)
            r.expire(f"blocked_logged:http:{ip}", 600)

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

    HTTP_PORT = int(os.getenv("HTTP_PORT", 8080))

    # La mejor práctica en aiohttp para soportar ambos es usar "::" 
    # y dejar que el SO maneje el mapeo de IPv4 automáticamente.
    site = web.TCPSite(runner, "::", HTTP_PORT)
    
    try:
        await site.start()
        print(f"[+] HTTP honeypot Dual-Stack escuchando en port {HTTP_PORT} (IPv4/IPv6)")
    except Exception as e:
        # Fallback por si IPv6 no está habilitado en el sistema
        print(f"[!] IPv6 falló, intentando solo IPv4: {e}")
        site_v4 = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
        await site_v4.start()

    # No necesitas un while True con sleep. 
    # runner mantiene la app viva, pero para no salir de la función:
    await asyncio.Event().wait()
