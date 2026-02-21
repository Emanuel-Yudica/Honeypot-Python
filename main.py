from multiprocessing import Process, Queue
import os
#from celery_worker.watcher import watch
# from servers.ssh_server import run_ssh_server
# from servers.http_server import run_http_server
from ssh_server import run_ssh_server
from http_server import run_http_server
from parser import parser
import asyncio
from celery_worker.watcher import watch_multiple

def run_ssh(q):
    print("[+] SSH process started")
    asyncio.run(run_ssh_server(q))

def run_http(q):
    print("[+] HTTP process started")
    asyncio.run(run_http_server(q))

# def run_watcher_http():
#     print("[+] Watcher HTTP started")
#     from celery_worker.watcher import watch
#     watch("http_log.json")

# def run_watcher_ssh():
#     print("[+] Watcher SSH started")
#     from celery_worker.watcher import watch
#     watch("ssh_log.json")
def run_watcher():
    watch_multiple(["http_log.json", "ssh_log.json"])

def delete_files():
    if os.path.exists("http_log.json"):
        os.remove("http_log.json")
    os.mknod("http_log.json")
    if os.path.exists("ssh_log.json"):
        os.remove("ssh_log.json")
    os.mknod("ssh_log.json")
if __name__ == "__main__":
    delete_files()
    q = Queue()

    ssh = Process(target=run_ssh, args=(q,))
    http = Process(target=run_http, args=(q,))
    parser_proc = Process(target=parser, args=(q,))
    # watcher_http_proc = Process(target=run_watcher_http)
    # watcher_ssh_proc = Process(target=run_watcher_ssh)
    watcher_proc = Process(target=run_watcher)
    ssh.start()
    http.start()
    parser_proc.start()
    #watcher_ssh_proc.start()
    watcher_proc.start()

    ssh.join()
    http.join()
    parser_proc.join()
    watcher_proc.join() 
    #watcher_http_proc.join()
