# Final-computacion-2

La idea de este proyecto es crear un honeypot utilizando los conceptos aprendidos en la materia durante el cursado.

El programa consiste en la ejecucion de un servidor HTTP y SSH. 

Al final de la ejecución, se genera un reporte en formato HTML que incluye la información de las solicitudes HTTP y SSH, así como la lista de rutas más utilizadas y las contraseñas más utilizadas.

El proyecto usa tecnologías como Redis, Celery, Paramiko, aiohttp, mecanismos de IPC(queues) y conexion a los servicios de correo electrónico.

Ademas este proyecto incluye una implementacion con docker-compose.

## Arquitectura del proyecto

![](https://github.com/Eyudica/Final-computacion-2--Honeypot/blob/main/new_architecture.png)

## Configuración y Ejecución Local

### Prerequisitos
- Python 3.8+
- Redis Server

### Instalación de Dependencias
Iniciar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate
```
Instala las dependencias de Python:
```bash
pip install -r requirements.txt
```

### Ejecución
Para iniciar el honeypot localmente, sigue estos pasos:

1.  Inicia el servidor Redis:
    ```bash
    redis-server
    ```

2.  Inicia el worker de Celery:
    ```bash
    PYTHONPATH=$(pwd) celery -A celery_app.app worker --loglevel=info
    ```

3.  Inicia la aplicación principal:
    ```bash
    python main.py -h
    ```

## Ejecución con Docker Compose

Para ejecutar el honeypot utilizando Docker Compose, asegúrate de tener Docker y Docker Compose instalados.

1.  Construye y levanta los servicios:
    ```bash
    docker-compose up --build
    ```

2.  Para detener los servicios:
    ```bash
    docker-compose down
    ```