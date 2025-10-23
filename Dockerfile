# Imagen base: Python liviano
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para geopandas y shapely
RUN apt-get update && apt-get install -y \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero (mejor cache de Docker)
COPY requirements2.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto al contenedor
COPY . /app

# Dar permisos al script de inicio
RUN chmod +x start_api_prueba_docker.sh

# Exponer el puerto de la API
EXPOSE 8000

# Comando por defecto para levantar la API
CMD ["./start_api_prueba_docker.sh"]
