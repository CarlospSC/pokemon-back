# Usar una imagen oficial de Python, asegúrate de usar la versión correcta
FROM python:3.13.0

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de dependencias a la imagen
COPY requirements.txt .

# Instalar las dependencias en el contenedor
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente de la app al contenedor
COPY . .

# Exponer el puerto que usa FastAPI (8000)
EXPOSE 8000

# Comando para ejecutar la aplicación FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
