FROM python:3.10-slim

# 1️⃣ Installa pacchetti di sistema minimi necessari
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ Imposta la working directory
WORKDIR /app

# 3️⃣ Copia solo i file di dipendenze per sfruttare il caching
COPY requirements.txt .

# 4️⃣ Installa prima llama-cpp-python per LLM locale
RUN pip install --upgrade pip && \
    pip install llama-cpp-python && \
    pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copia il resto del backend (codice + modelli)
COPY . .

# 6️⃣ (opzionale) Scarica risorse NLTK se le usi
RUN python -m nltk.downloader punkt

# 7️⃣ Espone la porta FastAPI
EXPOSE 8000

# 8️⃣ Avvia l'app FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
