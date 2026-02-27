import os
import asyncio
import paramiko
import redis
import sys
import socket # Nueva importación
from datetime import datetime # Nueva importación

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Cargar o generar la clave del servidor SSH
HOST_KEY_PATH = "server.key"
if not os.path.exists(HOST_KEY_PATH):
    print(f"[*] Generando nueva clave SSH en {HOST_KEY_PATH}...")
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(HOST_KEY_PATH)
HOST_KEY = paramiko.RSAKey(filename=HOST_KEY_PATH)

class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip,q):
        self.client_ip = client_ip
        self.q=q

    def check_auth_password(self, username, password):
        self.q.put({
                "server": "SSH",
                "ip": self.client_ip,
                "user": username,
                "password": password,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
            })

        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

def handle_client_blocking(client, addr, q):
    ip = addr[0]
    
    # Aunque quites tu lógica de Redis, esta línea es VITAL para Paramiko
    client.setblocking(True) 

    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)
    
    # Tu clase SSHServer que mete datos en la Queue
    server = SSHServer(ip, q)

    try:
        transport.start_server(server=server)
        # Esperamos a que la autenticación ocurra (o falle)
        # .join() bloquea este hilo del executor hasta que el cliente se desconecte
        transport.join() 
    except Exception as e:
        print(f"[!] Error con {ip}: {e}")
    finally:
        transport.close()
        client.close()


async def run_ssh_server(q):
    loop = asyncio.get_running_loop()
    SSH_PORT = int(os.getenv("SSH_PORT", 2222))

    # Intentar configurar un único socket Dual Stack (IPv6 + IPv4)
    try:
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # IPV6_V6ONLY = 0 permite recibir IPv4 en este mismo socket
        server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        server.bind(("::", SSH_PORT))
        server.listen()
        server.setblocking(False)
        print(f"[+] SSH Honeypot Dual-Stack escuchando en puerto {SSH_PORT} (IPv4/IPv6)")
    except Exception as e:
        print(f"[!] Error creando socket Dual-Stack: {e}")
        # Si falla el dual-stack, podrías reintentar solo con IPv4 aquí
        return

    while True:
        # Aceptar conexiones de forma sencilla
        client, addr = await loop.sock_accept(server)
        
        # Ejecutar el manejo bloqueante de Paramiko en un hilo aparte
        loop.run_in_executor(
            None,
            handle_client_blocking,
            client,
            addr,
            q
        )



# asyncio.run(main())
