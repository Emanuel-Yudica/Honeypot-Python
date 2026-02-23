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

    if r.exists(f"blocked:{ip}"):

        if r.setnx(f"blocked_logged:ssh:{ip}", 1):

            print(f"[BLOCKED SSH] {ip}")

            r.expire(f"blocked_logged:ssh:{ip}", 600)

        client.close()
        return

    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)

    server = SSHServer(ip, q)

    try:
        transport.start_server(server=server)

        while transport.is_active():
            pass

    except Exception as e:
        print(f"[!] Error con {ip}: {e}")

    finally:
        transport.close()
        client.close()


async def run_ssh_server(q):
    loop = asyncio.get_running_loop()

    server = socket.create_server(("0.0.0.0", 2222),family=socket.AF_INET6,dualstack_ipv6=True,reuse_port=True)
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
