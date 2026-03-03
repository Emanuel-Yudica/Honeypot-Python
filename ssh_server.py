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
    
    sock_v4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_v4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_v4.bind(("0.0.0.0", SSH_PORT))
    sock_v4.listen()
    sock_v4.setblocking(False)

    try:
        sock_v6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock_v6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Forzamos que este socket SOLO escuche IPv6
        sock_v6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        sock_v6.bind(("::", SSH_PORT))
        sock_v6.listen()
        sock_v6.setblocking(False)
        print(f"[+] SSH escuchando en IPv6 ([::]:{SSH_PORT})")
    except Exception as e:
        sock_v6 = None
        print(f"[!] No se pudo iniciar IPv6 para SSH: {e}")

    print(f"[+] SSH escuchando en IPv4 (0.0.0.0:{SSH_PORT})")

    # Función interna para aceptar conexiones
    async def accept_connections(sock):
        while True:
            client, addr = await loop.sock_accept(sock)
            # Al ser independientes, addr[0] vendrá como "127.0.0.1" o "::1" sin prefijos
            loop.run_in_executor(
                None,
                handle_client_blocking,
                client,
                addr,
                q
            )

    # Creamos las tareas para ambos sockets
    tasks = [accept_connections(sock_v4)]
    if sock_v6:
        tasks.append(accept_connections(sock_v6))

    # Ejecutamos ambas tareas en paralelo
    await asyncio.gather(*tasks)