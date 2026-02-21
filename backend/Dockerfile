# ---- base image -------------------------------------------------
FROM python:3.10-slim AS base
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off

# ---- system dependencies (C++ compilers, cmake, etc.) -----------

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    libgomp1 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----------------------------------------
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# ---- Application files ------------------------------------------
COPY . .

# ---- Entrypoint -------------------------------------------------
RUN chmod +x entrypoint.sh
ENTRYPOINT ["bash", "./entrypoint.sh"]
