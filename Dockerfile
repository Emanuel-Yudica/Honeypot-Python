# Usa una imagen oficial de Python como imagen base
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de dependencias y lo instala
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Exponer los puertos que utiliza la aplicación
EXPOSE 8000 2222

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
