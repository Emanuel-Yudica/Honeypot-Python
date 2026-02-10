import asyncio
import socket
import paramiko
from datetime import datetime
HOST_KEY = paramiko.RSAKey(filename="server.key")


class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip,q):
        self.client_ip = client_ip
        self.q=q

    def check_auth_password(self, username, password):
        time=datetime.now()
        formatted_time=time.strftime("%Y-%m-%d %H:%M:%S")
        self.q.put({
                "server": "SSH",
                "ip": self.client_ip,
                "user": username,
                "password": password,
                "time": formatted_time
            })

        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

def handle_client_blocking(client, addr, q):
    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)

    server = SSHServer(addr[0], q)

    try:
        transport.start_server(server=server)
        while transport.is_active():
            pass
    except Exception as e:
        print(f"[!] Error con {addr[0]}: {e}")
    finally:
        transport.close()
        client.close()

async def run_ssh_server(q):
    loop = asyncio.get_running_loop()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 2222))
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
