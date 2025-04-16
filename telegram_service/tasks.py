from celery import shared_task
import requests
from django.conf import settings


@shared_task
def send_telegram_message_task(text: str):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("[Telegram] Missing token or chat ID.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        requests.post(url, data=payload, timeout=5)
    except requests.RequestException as e:
        print(f"[Telegram] Failed to send message: {e}")
