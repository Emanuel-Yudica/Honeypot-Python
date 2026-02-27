import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .tasks import process_event
import os
class HoneypotLogHandler(FileSystemEventHandler):
    def __init__(self, files_to_watch):
        self.files_to_watch = files_to_watch
        self.positions = {f: os.path.getsize(f) for f in files_to_watch if os.path.exists(f)}

    def on_modified(self, event):
        # Si el archivo modificado está en nuestra lista de vigilancia
        if event.src_path.endswith(tuple(self.files_to_watch)):
            self.process_new_lines(event.src_path)

    def process_new_lines(self, filepath):
        with open(filepath, "r") as f:
            # Vamos a la última posición leída
            f.seek(self.positions.get(filepath, 0))
            
            line = f.readline()
            while line:
                if line.strip(): # Evitar líneas vacías
                    try:
                        data = json.loads(line)
                        process_event.delay(data) # Enviar a Celery
                    except json.JSONDecodeError:
                        pass # Línea incompleta, se leerá en el próximo evento
                line = f.readline()
            
            # Guardamos la nueva posición
            self.positions[filepath] = f.tell()

def watch_multiple(files):
    # Configuramos el manejador y el observador
    event_handler = HoneypotLogHandler(files)
    observer = Observer()
    
    # Observamos el directorio actual "."
    observer.schedule(event_handler, path=".", recursive=False)
    
    print(f"[+] Watchdog activo vigilando: {files}")
    observer.start()
    
    try:
        while True:
            time.sleep(1) # El bucle principal no hace nada, solo mantiene vivo el proceso
    except KeyboardInterrupt:
        observer.stop()
    observer.join()










# def watch_multiple(files):

#     positions = {file: 0 for file in files}

#     while True:
#         for file in files:

#             with open(file, "r") as f:

#                 f.seek(positions[file])

#                 line = f.readline()

#                 while line:

#                     event = json.loads(line)

#                     process_event.delay(event)

#                     line = f.readline()

#                 positions[file] = f.tell()
#         time.sleep(0.1)


#bibilioteca para ver archivos sin bucle