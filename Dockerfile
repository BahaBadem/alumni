# ==============================================================================
# ALUMNI PORTAL - DOCKERFILE
# ==============================================================================
FROM python:3.11-slim

# Python çıktı tamponlamasını kapat ve bytecode (.pyc) yazımını devre dışı bırak
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını yükle (PostgreSQL istemcisi ve derleme araçları)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Proje kaynak kodlarını kopyala
COPY . /app/

# Portu dışa aç
EXPOSE 8000

# Varsayılan başlangıç komutu
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
