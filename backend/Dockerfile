FROM python:3.11-slim

# Imposta directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema (prima, perché raramente cambiano)
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia solo requirements per sfruttare la cache
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice (solo se è cambiato)
COPY . .

# Scarica risorse nltk (solo la prima volta)
RUN python -m nltk.downloader punkt

# Espone la porta dell'app
EXPOSE 8000

# Comando di avvio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
