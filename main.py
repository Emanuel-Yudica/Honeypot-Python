import os
import redis
import asyncio
import signal
import sys
from multiprocessing import Process, Queue

from ssh_server import run_ssh_server
from http_server import run_http_server
from parser import parser
from celery_worker.watcher import watch_multiple
from redis_functions import redis_get_keys
from redis_functions import ip_connection_watcher
import argparse
from send_summary import send_email
import datetime
from send_summary import *



# --- Conexión a Redis ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


arg_parser = argparse.ArgumentParser(description='Welcome to the honeypot. The goal is to run an HTTP and SSH server and obtain the most frequently tested paths and passwords. You can provide your email address to receive this summary.')

arg_parser.add_argument('--ssh', type=int, default=5,
                        help='Number of top ssh requests to show (default 5).')
arg_parser.add_argument('--http', type=int, default=5,
                        help='Number of top http requests to show (default 5).')
arg_parser.add_argument('--email', type=str,help='Email address to send summary (not required)')
arg_parser.add_argument('--filename', type=str,help='Filename to save summary .html (not required)')
args = arg_parser.parse_args()



# Guardamos el PID del padre para que los hijos no cierren nada
PARENT_PID = os.getpid()

def handler(signum, frame, processes):
    main(processes)

    sys.exit(0)
def main(processes):

    if os.getpid() != PARENT_PID:
        return
    end_time = datetime.datetime.now()
    end_time=end_time.strftime("%H:%M:%S")
    ips=r.smembers("ips")
    # --- LÓGICA DE REDIS ---
    if redis_get_keys(args.ssh, args.http):
        ssh_dict, http_dict = redis_get_keys(args.ssh, args.http)
    else:
        ssh_dict, http_dict = {}, {}
        return
# En main.py, dentro de la función main()
    html_reporte = generate_full_html(
        passwords_dict=ssh_dict, 
        rutas_dict=http_dict, 
        top_n=args.http, 
        ips_unicas=ips,  
        start_time=start_time, 
        end_time=end_time
    )
    if args.email:    
        send_mail=input("¿Desea enviar el reporte por email? (S/N)")
        if send_mail.lower()=="s":
            send_email(
                subject="Resumen de actividad de la sesion del honeypot",
                recipients=args.email,
                html_body=html_reporte
            )
        else:
            save_to_html_file(html_reporte,args.filename)
    else:
        save_to_html_file(html_reporte,args.filename)
        

    for p in processes:
        if p.is_alive():
            print(f"[*] Deteniendo {p.name} [PID: {p.pid}]...")
            p.terminate()

    for p in processes:
        p.join(timeout=1)
        if p.is_alive():
            p.kill() # Tiro de gracia si no cerró
def run_ssh(q):
    print(f"[+] SSH iniciado (PID: {os.getpid()})")
    try:
        asyncio.run(run_ssh_server(q))
    except KeyboardInterrupt:
        sys.exit(0) 
def run_http(q):
    print(f"[+] HTTP iniciado (PID: {os.getpid()})")
    try:
        asyncio.run(run_http_server(q))
    except KeyboardInterrupt:
        sys.exit(0) # Salir limpiamente del proceso hijo HTTP

# --- MAIN ---
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    start_time=start_time.strftime("%H:%M:%S")


    for f in ["http_log.json", "ssh_log.json"]:
        if os.path.exists(f): os.remove(f)
        open(f, 'a').close()

    q = Queue()

    procs = [
        Process(target=run_ssh, args=(q,), name="SSH-Server"),
        Process(target=run_http, args=(q,), name="HTTP-Server"),
        Process(target=parser, args=(q,), name="Log-Parser"),
        Process(target=watch_multiple, args=(["http_log.json", "ssh_log.json"],), name="Watcher"),
        Process(target=ip_connection_watcher, name="IP-Connection-Watcher")
        ]

    #Configurar señal con el filtro de PID
    signal.signal(signal.SIGINT, lambda s, f: handler(s, f, procs))

    for p in procs:
        p.start()

    for p in procs:
        p.join()