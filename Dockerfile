# Imagen base: Python liviano
FROM python:3.11-slim

# Definir directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todo el proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Dar permisos al script de inicio (si lo usás)
RUN chmod +x start_api.sh

# Exponer el puerto de la API
EXPOSE 8000

# Comando por defecto para levantar la API
CMD ["./start_api.sh"]
