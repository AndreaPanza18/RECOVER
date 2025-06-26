# 🚀 RECOVER - Automatic Functional Requirement Extraction

**RECOVER** is a tool for automatically extracting functional requirements from textual conversations and converting them into user stories. It provides a modern web interface and a FastAPI backend powered by LLMs.

---

## ✨ Requirements

* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* [Git LFS](https://git-lfs.github.com/)

> ⚠️ Make sure to run `git lfs install` **before** cloning the project, to ensure large model files are fetched correctly.

---

## 📅 Clone and Start the Project

```bash
git clone https://github.com/your-username/RECOVER.git
cd RECOVER
git lfs install
git lfs pull
```

---

## 💾 NLP Models

Models are located in `backend/models/` and are tracked via **Git LFS**:

* `fasttext_model.bin`
* `model.pkl`

> 🧠 If the clone fails for files >100MB, ensure Git LFS is correctly configured:
>
> ```bash
> git lfs install
> git lfs pull
> ```

> If you have issues with LFS or want to use a custom model (e.g., LLaMA 2), you can **manually download the model file** by defining a `.env` variable.

### 📥 Manual Model Download (Optional)

You can define a `.env` file in the `backend/` directory to specify a custom LLM model URL:

```env
# backend/.env
LLM_MODEL_URL= https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
```

Then run this command from the root of the project (or from within your Python venv):

```bash
python -c "import os, urllib.request; from dotenv import load_dotenv; load_dotenv(dotenv_path='backend/.env'); url=os.getenv('LLM_MODEL_URL'); p='backend/models/llama-2-7b-chat.Q4_K_M.gguf'; os.makedirs(os.path.dirname(p), exist_ok=True); urllib.request.urlretrieve(url, p) if url and not os.path.exists(p) else print('Model already exists or URL is missing')"
```

This ensures the model is locally available in `backend/models/` before building the Docker image, avoiding download during build time.## 🔐 Hugging Face Access Token (Required)

To use the LLaMA 2 model from Hugging Face, you must generate a **free access token**.

### 📌 Steps to create and use the token

1. Go to [https://huggingface.co](https://huggingface.co) and sign in (or register).
2. Navigate to your token settings:
   👉 [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Click **“New token”**, give it a name (e.g. `recover-access`), and choose **“Read”** permissions.
4. Copy the generated token.

### 🧪 Store the token in a `.env` file inside the `RECOVER/backend` directory

```env
HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 🚀 Run the Project with the Token

Once the `.env` file is in place, simply run:

```bash
docker-compose up --build
```

The token will be passed into the container environment and used to authenticate with Hugging Face APIs when downloading the LLaMA model.

---

Access the frontend (React app) at:

```
http://localhost:3000
```

The backend API (FastAPI) is available at:

```
http://localhost:8000
```
