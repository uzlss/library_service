# 📚 Library Service

A Django-based backend application for managing a book borrowing system with integrated Telegram notifications and Celery task processing.

---

## 🚀 Features

- 📖 Book and borrowing management
- 👤 User-specific borrowing history
- ✅ Admin functionality for all borrowings
- 🔔 Telegram bot notifications on borrowing creation
- ⏱ Asynchronous task queue with Celery + Redis
- 🔒 JWT authentication
- 🧪 Test coverage for key business logic

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
SECRET_KEY=your-django-secret
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-group-or-channel-id
```

---
## 🔔 Telegram Notifications

When a borrowing is created or returned, a formatted message is sent to the configured Telegram chat. This is handled asynchronously by a **Celery task**.

Example message:

```
📚 Borrowing Created
👤 User: Igor (igor@example.com)
📖 Book: The Pragmatic Programmer
📅 Expected Return: 2025-04-30
```
---

## 🧵 Celery Setup (Windows Compatible)

### 1. Start Redis (if not running):

```bash
docker run -d -p 6379:6379 redis
```

### 2. Start the Celery worker:

```bash
celery -A library_service worker --loglevel=info --pool=solo
```

> ⚠️ On Windows, you must use `--pool=solo`

---
## 📦 Stack

- Django + DRF
- SQLite
- Celery + Redis
- Telegram Bot API

---