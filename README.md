# RECOVER - Guida all'Installazione

**RECOVER** è uno strumento per l'estrazione automatica di requisiti funzionali da conversazioni testuali. Questa guida ti aiuterà a installarlo e avviarlo correttamente.

---

## ✨ Requisiti

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git LFS](https://git-lfs.github.com/)

> ⚠️ Assicurati di aver eseguito `git lfs install` **prima** del clone, per scaricare i modelli correttamente.

---

## 📂 Clona e avvia il progetto

```bash
# Clona il repository (Git LFS attivo)
git clone https://github.com/tuo-utente/RECOVER.git
cd RECOVER

# Installa Git LFS se non l'hai ancora fatto (solo una volta)
git lfs install

# Scarica i file gestiti da LFS (modelli)
git lfs pull

# Avvia tutto con Docker Compose
docker-compose up --build
```

Accedi all'app React su:
```
http://localhost:3000
```

Il backend FastAPI risponde su:
```
http://localhost:8000
```

---

## 💾 Modelli NLP

I modelli vengono salvati in `backend/models/` e sono tracciati con **Git LFS**.

- `fasttext_model.bin`
- `model.pkl`

> Se il clone fallisce per file >100MB, assicurati di avere Git LFS attivo:
> ```bash
> git lfs install
> git lfs pull
> ```

