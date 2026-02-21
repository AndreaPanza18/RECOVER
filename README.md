# 🚀 RECOVER - Automatic Functional Requirement Extraction

**RECOVER** is a tool for automatically extracting functional requirements from textual conversations and converting them into user stories. It provides a modern web interface and a FastAPI backend powered by LLMs.

---

## ✨ Requirements

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)

> ⚠️ Make sure to have at least 16 gigabyte of ram on your machine, in order to run the software.

---

## 📅 Clone Project

```bash
git clone https://github.com/gianwario/RECOVER.git
cd RECOVER
```

---

## 📃 Create an .env file

Go in RECOVER/backend/ and create a .env  
In this file you have to insert your personal Chat GPT and Gemini API keys.  
Here yuo can create your personal keys:
- [Chat GPT](https://platform.openai.com/api-keys)
- [Gemini](https://aistudio.google.com/api-keys)

Your file has to be like:
```bash
GOOGLE_API_KEY: your Key
OPENAI_API_KEY: your Key
```
> ⚠️ Use exactly *GOOGLE_API_KEY* and *OPENAI_API_KEY*

---

## 🐳 Open Docker Desktop
Open a terminal in RECOVER/backend/ and use this command:
```bash
docker-compose build
```

Once the build is complete, you'll see in the Docker Desktop, in section volumes, the RECOVER frontend and backend.

Now you can use the command:
```bash
docker-compose up
```

Now you can use RECOVER!

---

## ⚠️ ATTENTION
If you had problem in the download of the models, you can easly recover them here:
- [Hugging Face](https://huggingface.co/AndreaPanza18/RECOVER-models)

You can manualy download them and insert in backend/models  






