import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from database import SessionLocal
from models import Alert
from services.bybit import get_ticker
from services.telegram import send_telegram_message


def check_alerts_once():
    db = SessionLocal()

    try:
        # Берём только алерты, по которым уведомление ещё не отправлено
        alerts = db.scalars(
            select(Alert).where(
                Alert.notified_at.is_(None)
            )
        ).all()

        prices = {}

        for alert in alerts:
            symbol = alert.symbol.upper()

            try:
                # Для одинаковой монеты не запрашиваем цену несколько раз
                if symbol not in prices:
                    ticker = get_ticker(
                        symbol=symbol,
                        category="spot"
                    )
                    prices[symbol] = ticker["price"]

                current_price = prices[symbol]

            except Exception as error:
                print(
                    f"Ошибка получения цены {symbol}: {error}"
                )
                continue

            if alert.direction == "above":
                condition_met = current_price >= alert.target_price
            else:
                condition_met = current_price <= alert.target_price

            # Первое срабатывание
            if condition_met and not alert.is_triggered:
                alert.is_triggered = True
                alert.triggered_at = datetime.now(timezone.utc)

                db.commit()
                db.refresh(alert)

                print(
                    f"Алерт {alert.id} сработал: "
                    f"{symbol} {current_price}"
                )

            # Отправляем Telegram только один раз
            if alert.is_triggered and alert.notified_at is None:
                direction_text = (
                    "выше"
                    if alert.direction == "above"
                    else "ниже"
                )

                message = (
                    "🚨 Сработал ценовой алерт!\n\n"
                    f"Монета: {alert.symbol}\n"
                    f"Условие: {direction_text} "
                    f"{alert.target_price} USDT\n"
                    f"Текущая цена: {current_price} USDT"
                )

                try:
                    sent = send_telegram_message(message)

                    if sent:
                        alert.notified_at = datetime.now(timezone.utc)

                        db.commit()
                        db.refresh(alert)

                        print(
                            f"Telegram отправлен: alert_id={alert.id}"
                        )

                except Exception as error:
                    print(
                        f"Ошибка Telegram "
                        f"для alert_id={alert.id}: {error}"
                    )

    finally:
        db.close()


async def alert_worker():
    print("🔄 Автоматическая проверка алертов запущена")

    while True:
        try:
            await asyncio.to_thread(check_alerts_once)

        except Exception as error:
            print(
                f"Ошибка фоновой проверки: {error}"
            )

        await asyncio.sleep(60)