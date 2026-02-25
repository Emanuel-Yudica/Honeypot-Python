import os
import redis
import asyncio
import signal
import sys
import multiprocessing
from multiprocessing import Process, Queue

from ssh_server import run_ssh_server
from http_server import run_http_server
from parser import parser
from celery_worker.watcher import watch_multiple
from redis_functions import redis_get_keys
import argparse
from send_mail import send_email
import datetime
# --- Conexión a Redis ---
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


arg_parser = argparse.ArgumentParser(description='Welcome to the honeypot. The goal is to run an HTTP and SSH server and obtain the most frequently tested paths and passwords. You will need to provide your email address to receive this summary.')

arg_parser.add_argument('--ssh', type=int, default=5,
                        help='Number of top ssh requests to show(default 5).')
arg_parser.add_argument('--http', type=int, default=5,
                        help='Number of top http requests to show(default 5).')
arg_parser.add_argument('--email', type=str,required=True,help='Email address to send summary')
args = arg_parser.parse_args()



# Guardamos el PID del padre para que los hijos no cierren nada
PARENT_PID = os.getpid()

def handler(signum, frame, processes):
    main(processes)

    print("\n[+] Sistema cerrado limpiamente.")
    sys.exit(0)
def main(processes):
    # Si el proceso actual NO es el padre, no hace nada (evita el AssertionError)
    if os.getpid() != PARENT_PID:
        return

    # --- LÓGICA DE REDIS ---
    if redis_get_keys(args.ssh, args.http):
        ssh_dict, http_dict = redis_get_keys(args.ssh, args.http)
    else:
        print("No se encontraron credenciales ni rutas, no hay resumen para mostrar")
        return
    send_mail=input("¿Desea enviar un correo con los datos obtenidos? (S/N): ")
    if send_mail.lower() == "s":

        send_email(
            subject="Resumen de actividad de la sesion del honeypot",
            passwords_dict=ssh_dict,
            rutas_dict=http_dict,
            top_n=10,  # puede ser mayor que la cantidad real
            recipients=args.email
        )
    else:
        date=datetime.date.today()
        filename=f"summary_data_{date}.txt"
        print(f"Las credenciales y rutas más utilizadas fueron obtenidas y guardadas en el archivo 'summary_data_{date}.txt'.")
        
        with open(filename, "w") as f:
            f.write(f"Se deja un resumen de las top {args.ssh} credenciales y {args.http} rutas más utilizadas en el honeypot.\n\n")
            f.write(f"SSH:\n{ssh_dict}\n\nHTTP:\n{http_dict}")

    # --- CIERRE DE PROCESOS ---
    print("\n[!] Terminando procesos hijos...")
    for p in processes:
        if p.is_alive():
            print(f"[*] Deteniendo {p.name} [PID: {p.pid}]...")
            p.terminate()

    # Espera y limpieza final
    for p in processes:
        p.join(timeout=1)
        if p.is_alive():
            p.kill() # Tiro de gracia si no cerró
# --- Wrappers de ejecución ---
def run_ssh(q):
    print(f"[+] SSH iniciado (PID: {os.getpid()})")
    try:
        asyncio.run(run_ssh_server(q))
    except KeyboardInterrupt:
        pass

def run_http(q):
    print(f"[+] HTTP iniciado (PID: {os.getpid()})")
    try:
        asyncio.run(run_http_server(q))
    except KeyboardInterrupt:
        pass

# --- MAIN ---
if __name__ == "__main__":
    # 1. Limpiar archivos
    for f in ["http_log.json", "ssh_log.json"]:
        if os.path.exists(f): os.remove(f)
        open(f, 'a').close()

    q = Queue()

    # 2. Definir procesos
    procs = [
        Process(target=run_ssh, args=(q,), name="SSH-Server"),
        Process(target=run_http, args=(q,), name="HTTP-Server"),
        Process(target=parser, args=(q,), name="Log-Parser"),
        Process(target=watch_multiple, args=(["http_log.json", "ssh_log.json"],), name="Watcher")
    ]

    # 3. Configurar señal con el filtro de PID
    signal.signal(signal.SIGINT, lambda s, f: handler(s, f, procs))

    # 4. Arrancar
    for p in procs:
        p.start()

    # 5. Mantener vivo el proceso principal
    try:
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        pass