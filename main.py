from multiprocessing import Process, Queue
# from servers.ssh_server import run_ssh_server
# from servers.http_server import run_http_server
from ssh_server import run_ssh_server
from http_server import run_http_server
from parser import parser
import asyncio

def run_ssh(q):
    print("[+] SSH process started")
    asyncio.run(run_ssh_server(q))

def run_http(q):
    print("[+] HTTP process started")
    asyncio.run(run_http_server(q))

if __name__ == "__main__":
    q = Queue()

    ssh = Process(target=run_ssh, args=(q,))
    http = Process(target=run_http, args=(q,))
    parser_proc = Process(target=parser, args=(q,))

    ssh.start()
    http.start()
    parser_proc.start()

    ssh.join()
    http.join()
