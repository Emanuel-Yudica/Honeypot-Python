import asyncio
import socket
import paramiko
import redis
from datetime import datetime
HOST_KEY = paramiko.RSAKey(filename="server.key")
r=redis.Redis(host="localhost", port=6379, db=0)

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

    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    server.bind(("::", 2222))
    server.listen()
    server.setblocking(False)

    print("[+] SSH server asyncio escuchando en puerto 2222")

    while True:
        client, addr = await loop.sock_accept(server)

        loop.run_in_executor(
            None,
            handle_client_blocking,
            client,
            addr,
            q
        )



# asyncio.run(main())
