# import json
# def check_ddos(service): # prodria leer el archivo del log y agarrar todas las requests de esta ip y que se 
#     #fije entre cada una el tiempo qeu hubo entre medio y si es menor a 3 segundos entre 50 requests, lo bloquea
#     tolerancia=0
#     while True:

#     pass
from celery_app.app import app
import redis
r = redis.Redis(host="localhost", port=6379, db=0) #escalar
# TIEMPO=30
# TOLERANCIA=100

@app.task # para que lo tome como tarea de celery


def process_event(event):


    server = event.get("server")
    
    if server == "SSH":
        password = event.get("password", "unknown")
        # Redis creará la clave si no existe e incrementará
        r.incr(f"ssh_password_count:{password}")
        
    elif server == "HTTP":
        path = event.get("path", "unknown")
        r.incr(f"http_path_count:{path}")
    # ip = event["ip"]

    # key = f"rate:{ip}"

    # # incrementa contador
    # count = r.incr(key)

    # # si es la primera vez, setea expiración
    # if count == 1:
    #     r.expire(key, TIEMPO)

    # print(f"{ip} hizo {count} requests en {TIEMPO} segundos")

    # if count > TOLERANCIA:
    #     r.set(f"blocked:{ip}", 1)
    #     r.expire(f"blocked:{ip}", 600) # expira en 10 minutos el bloqueo
    #     event_blocked_count = r.incr(f"blocked_in_hour:{ip}")
    #     if event_blocked_count == 1:
    #         r.expire(f"blocked:{ip}", 3600)
    #     if event_blocked_count ==5:
            
    #         send_email(
    #             subject="Alerta de seguridad",
    #             body=f"La IP {ip} ha sido bloqueada 5 veces en la ultima hora",
    #             recipients=["emanuelyudica2@gmail.com"],
    #         )
    # return count

#.ENV o constantes config