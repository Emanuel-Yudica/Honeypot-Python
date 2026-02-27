import os
import redis
import datetime
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def redis_get_keys(ssh_quantity=1, http_quantity=1):
    try:
        # Convertir a enteros por seguridad
    

        keys = r.keys("*")
        if not keys:
            print("Redis está vacío.")
            return

        ssh_keys = []
        http_keys = []

        for key in keys:
            if r.type(key) == "string":
                val = r.get(key)
                try:
                    counter = int(val)
                except (TypeError, ValueError):
                    continue  # Ignorar si no es numérico

                key_str = key

                if "ssh" in key_str.lower():
                    ssh_keys.append((key_str, counter))
                elif "http" in key_str.lower():
                    http_keys.append((key_str, counter))

        # Ordenar por contador descendente
        ssh_keys.sort(key=lambda x: x[1], reverse=True)
        http_keys.sort(key=lambda x: x[1], reverse=True)

        top_ssh={}
        for key, counter in ssh_keys[:ssh_quantity]:
            key=key.replace("ssh_password_count:", "")
            #print(f"{key} -> {counter}")
            top_ssh[key]=counter
        top_http={}
        for key, counter in http_keys[:http_quantity]:
            key=key.replace("http_path_count:", "")
            #print(f"{key} -> {counter}")
            top_http[key]=counter
        return top_ssh, top_http
    except Exception as e:
        print(f"Error al leer Redis: {e}")

def ip_connection_watcher():
    """Escucha el canal de Redis e imprime las conexiones al instante"""
    # Importante: decode_responses=True para leer texto directamente
    local_redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = local_redis.pubsub()
    
    # Nos suscribimos al canal donde el worker hace el r.publish
    pubsub.subscribe("canal_ips")
    
    print("\nEsperando conexiones...")
    ips_vistas = set()
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = message['data'] 
                ip = data.split(" -> ")[1]
                if ip not in ips_vistas:
                    hora = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{hora}] [NUEVA CONEXIÓN] -> {data}")
                    ips_vistas.add(ip)
    except KeyboardInterrupt:
        print("\n[!] Watcher detenido.")
        return