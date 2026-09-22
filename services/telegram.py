import os

import httpx
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены"
        )

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = httpx.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
        },
        timeout=10.0,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("ok", False)