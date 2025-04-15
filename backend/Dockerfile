FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    cmake \
    libopenblas-dev \
    libomp-dev \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY . .
RUN echo ls && ls models/

RUN echo "✅ Scarico il modello..." && \
    wget -O models/llama-2-7b-chat.Q4_K_M.gguf \
    https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf && \
    echo "✅ Contenuto di models/ dopo il download:" && \
    ls -lh models/

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install llama-cpp-python && \
    pip install -r requirements.txt

RUN python -m nltk.downloader punkt
RUN ls -lh models/
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
