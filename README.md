# 📚 Library Service

A Django-based backend application for managing a book borrowing system with integrated Telegram notifications and Celery task processing.

---

## 🚀 Features

- 📖 Book catalog with cover type, inventory, and daily fee
- 👤 User-specific borrowing history
- ✅ Admin functionality for all borrowings
- 🔔 Telegram bot notifications on borrowing creation
- ⏱ Asynchronous task queue with Celery + Redis
- 🔒 JWT authentication
- 🧪 Test coverage for key business logic
- 🐳 Dockerized setup with Postgres, Redis, Django and Celery

---

## ⚙️ Setup

### 1. Clone the repo

```sh
git clone https://github.com/uzlss/library_service.git
cd library_service
```

### 2. Create and activate virtual environment

```sh
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.sample` → `.env` and fill in values:

```env
POSTGRES_PASSWORD=POSTGRES_PASSWORD
POSTGRES_USER=POSTGRES_USER
POSTGRES_DB=POSTGRES_DB
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data
TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID
SECRET_KEY=SECRET_KEY
REDIS_HOST=redis://redis:6379/0
```

---
## 🔔 Telegram Notifications

When a borrowing is created or returned, a formatted message is sent to the configured Telegram chat. This is handled asynchronously by a **Celery task**.

Example message:

```
📚 Borrowing Created
👤 User: (igor@example.com)
📖 Book: The Pragmatic Programmer
📅 Expected Return: 2025-04-30
```
---

## 🧵 Celery Setup (Windows Compatible)

### 1. Start Redis (if not running):

```sh
docker run -d -p 6379:6379 redis
```

### 2. Start the Celery worker:

```sh
celery -A library_service worker --loglevel=info --pool=solo
```

> ⚠️ On Windows, you must use `--pool=solo`

---

## 🧵 Running with Docker + Celery

### Start everything

```bash
docker-compose up --build
```

### Services included

- Django app on `localhost:8000`
- PostgreSQL
- Redis
- Celery worker (auto-handles Telegram messages)

---
## 📦 Stack

- Django + DRF
- PostgreSQL or SQLite
- Celery + Redis
- Telegram Bot API
- Docker

---