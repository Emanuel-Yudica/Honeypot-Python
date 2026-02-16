# import json
# def check_ddos(service): # prodria leer el archivo del log y agarrar todas las requests de esta ip y que se 
#     #fije entre cada una el tiempo qeu hubo entre medio y si es menor a 3 segundos entre 50 requests, lo bloquea
#     tolerancia=0
#     while True:

#     pass
from celery_app.app import app
import redis
r = redis.Redis(host="localhost", port=6379, db=0)
TIEMPO=30
TOLERANCIA=100

@app.task # para que lo tome como tarea de celery


def process_event(event):

    ip = event["ip"]

    key = f"rate:{ip}"

    # incrementa contador
    count = r.incr(key)

    # si es la primera vez, setea expiración
    if count == 1:
        r.expire(key, TIEMPO)

    print(f"{ip} hizo {count} requests en {TIEMPO} segundos")

    if count > TOLERANCIA:
        r.set(f"blocked:{ip}", 1)
        r.expire("blocked:ip", 600) # expira en 10 minutos el bloqueo


    return count

