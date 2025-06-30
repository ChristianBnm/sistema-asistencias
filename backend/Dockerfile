FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero para cachear
COPY requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y netcat-openbsd bash && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copiar script y darle permisos
COPY esperar-mysql.sh /app/esperar-mysql.sh
RUN chmod +x /app/esperar-mysql.sh

# Copiar el resto del código (si no lo copias antes)
COPY . /app

EXPOSE 5000
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["bash", "/app/esperar-mysql.sh", "db", "3306", "python", "run.py"]



