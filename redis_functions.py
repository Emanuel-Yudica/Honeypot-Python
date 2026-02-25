import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

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