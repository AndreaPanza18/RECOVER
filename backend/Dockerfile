# ---- base image with CUDA and cuDNN dev runtime (Ubuntu 22.04) ----
# Switch to 'devel' image so build-essential and matching toolchain are available
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 AS base
WORKDIR /app

# Unbuffered Python and pip config
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off

# ---- system dependencies (C++ compilers, cmake, git, etc.) -----------
# Ensure HTTPS repos and keyring
RUN apt-get update && apt-get install -y --no-install-recommends \
    ubuntu-keyring \
    ca-certificates \
    apt-transport-https \
 && rm -rf /var/lib/apt/lists/*

# Install Python runtime, pip, and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3-pip \
    build-essential \
    cmake \
    git \
    libgomp1 \
    curl \
 && ln -sf /usr/bin/python3.10 /usr/bin/python \
 && ln -sf /usr/bin/pip3 /usr/bin/pip \
 && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----------------------------------------
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Application files ------------------------------------------
COPY . .

# ---- Download model script must be executable -------------------
RUN chmod +x download_model.sh

# ---- Expose port and entrypoint ---------------------------------
EXPOSE 8000
ENTRYPOINT ["bash", "./download_model.sh"]
