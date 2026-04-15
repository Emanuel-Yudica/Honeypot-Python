
El programa consiste en la ejecucion de un servidor HTTP y SSH. 

Al final de la ejecución, se genera un reporte en formato HTML que incluye la información de las solicitudes HTTP y SSH, así como la lista de rutas más utilizadas y las contraseñas más utilizadas.

El proyecto usa tecnologías como Redis, Celery, soporte IPV4/IPV6, Paramiko, aiohttp, mecanismos de IPC(queues) y conexion a los servicios de correo electrónico.


## Arquitectura del proyecto

![](https://github.com/Emanuel-Yudica/Honeypot-Python/blob/main/architecture.png)

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