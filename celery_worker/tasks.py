
from celery_app.app import app
import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True) # Configuración de Redis con variables de entorno

@app.task # para que lo tome como tarea de celery


def process_event(event):
    print(f"EVENTO: {event}")
    server = event.get("server")
    ip=event.get("ip")
    if server == "SSH":
        password = event.get("password", "unknown")

        r.incr(f"ssh_password_count:{password}")
        
    elif server == "HTTP":
        path = event.get("path", "unknown")
        r.incr(f"http_path_count:{path}")
    if ip:
        print(f"IP: {ip}")
        # Normalizar si viene de IPv6 dual-stack
        clean_ip = ip.replace("::ffff:", "") if ip.startswith("::ffff:") else ip
        r.sadd("ips", clean_ip)    # ip = event["ip"]
        r.publish("canal_ips", f"{server} -> {clean_ip}")

