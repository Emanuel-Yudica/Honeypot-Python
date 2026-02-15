from multiprocessing import Process, Queue
import os
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
def delete_files():
    if os.path.exists("http_log.json"):
        os.remove("http_log.json")
    if os.path.exists("ssh_log.json"):
        os.remove("ssh_log.json")
if __name__ == "__main__":
    delete_files()
    q = Queue()

    ssh = Process(target=run_ssh, args=(q,))
    http = Process(target=run_http, args=(q,))
    parser_proc = Process(target=parser, args=(q,))

    ssh.start()
    http.start()
    parser_proc.start()

    ssh.join()
    http.join()
