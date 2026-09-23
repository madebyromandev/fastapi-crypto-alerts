import asyncio
import os

import httpx
from dotenv import load_dotenv
from sqlalchemy import select

from database import SessionLocal
from models import Alert
from services.telegram import send_telegram_message


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_updates(offset=None):
    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    )

    params = {
        "timeout": 25
    }

    if offset is not None:
        params["offset"] = offset

    response = httpx.get(
        url,
        params=params,
        timeout=35.0
    )

    response.raise_for_status()

    return response.json().get("result", [])


def handle_command(text: str) -> str | None:
    parts = text.strip().split()

    if not parts:
        return None

    command = parts[0].lower()

    db = SessionLocal()

    try:
        # -------------------------
        # /start
        # -------------------------
        if command == "/start":
            return (
                "🤖 Crypto Alerts\n\n"
                "Команды:\n"
                "/alerts — список алертов\n"
                "/add BTC 90000 above — добавить алерт\n"
                "/add ETH 2500 below — добавить алерт\n"
                "/delete 7 — удалить алерт"
            )

        # -------------------------
        # /alerts
        # -------------------------
        if command == "/alerts":
            alerts = db.scalars(
                select(Alert).order_by(Alert.id)
            ).all()

            if not alerts:
                return "📭 Алертов пока нет."

            lines = ["📊 Мои алерты:\n"]

            for alert in alerts:
                if alert.notified_at is not None:
                    status = "✅"
                elif alert.is_triggered:
                    status = "🔔"
                else:
                    status = "⏳"

                direction = (
                    "выше"
                    if alert.direction == "above"
                    else "ниже"
                )

                lines.append(
                    f"{status} #{alert.id} "
                    f"{alert.symbol} — "
                    f"{direction} {alert.target_price} USDT"
                )

            return "\n".join(lines)

        # -------------------------
        # /add
        # -------------------------
        if command == "/add":
            if len(parts) != 4:
                return (
                    "Неверный формат.\n\n"
                    "Пример:\n"
                    "/add BTC 90000 above"
                )

            symbol = parts[1].upper()

            try:
                target_price = float(parts[2])
            except ValueError:
                return "❌ Цена должна быть числом."

            direction = parts[3].lower()

            if target_price <= 0:
                return "❌ Цена должна быть больше нуля."

            if direction not in ("above", "below"):
                return "❌ Направление: above или below."

            alert = Alert(
                symbol=symbol,
                target_price=target_price,
                direction=direction
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            direction_text = (
                "выше"
                if direction == "above"
                else "ниже"
            )

            return (
                "✅ Алерт создан\n\n"
                f"ID: {alert.id}\n"
                f"Монета: {symbol}\n"
                f"Условие: {direction_text} "
                f"{target_price} USDT"
            )

        # -------------------------
        # /delete
        # -------------------------
        if command == "/delete":
            if len(parts) != 2:
                return "Пример: /delete 7"

            try:
                alert_id = int(parts[1])
            except ValueError:
                return "❌ ID должен быть числом."

            alert = db.get(Alert, alert_id)

            if alert is None:
                return "❌ Алерт не найден."

            symbol = alert.symbol

            db.delete(alert)
            db.commit()

            return (
                f"🗑 Алерт #{alert_id} "
                f"{symbol} удалён."
            )

        return (
            "Неизвестная команда.\n\n"
            "Используй /start"
        )

    finally:
        db.close()


async def telegram_command_worker():
    print("🤖 Telegram-команды запущены")

    offset = None

    while True:
        try:
            updates = await asyncio.to_thread(
                get_updates,
                offset
            )

            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                chat_id = message.get(
                    "chat",
                    {}
                ).get("id")

                # Никто кроме твоего Telegram
                # управлять алертами не сможет
                if str(chat_id) != str(TELEGRAM_CHAT_ID):
                    continue

                text = message.get("text", "")

                if not text.startswith("/"):
                    continue

                reply = await asyncio.to_thread(
                    handle_command,
                    text
                )

                if reply:
                    await asyncio.to_thread(
                        send_telegram_message,
                        reply
                    )

        except asyncio.CancelledError:
            raise

        except Exception as error:
            print(
                f"Ошибка Telegram-команд: {error}"
            )

            await asyncio.sleep(5)