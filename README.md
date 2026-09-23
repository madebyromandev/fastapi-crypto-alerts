# 🚨 Crypto Alerts API

Backend-сервис для мониторинга цен криптовалют и отправки уведомлений в Telegram.

Проект получает актуальные цены через Bybit API, хранит ценовые алерты в PostgreSQL и автоматически проверяет их в фоновом режиме. Когда цена достигает заданного уровня, пользователь получает уведомление в Telegram.

## 🌐 Live Demo

Swagger API:

https://fastapi-crypto-alerts-production.up.railway.app/docs

## 🚀 Возможности

- Получение актуальной цены криптовалют через Bybit API
- Поддержка Spot и USDT Perpetual
- Создание ценовых алертов
- Изменение и удаление алертов
- PostgreSQL для хранения данных
- SQLAlchemy ORM
- Alembic migrations
- Автоматическая проверка цен в background worker
- Фиксация времени срабатывания алерта
- Защита от повторной отправки уведомлений
- Telegram-уведомления
- Управление алертами из Telegram
- Swagger / OpenAPI документация
- Развёртывание на Railway
- Работа 24/7 без локального компьютера

## 🤖 Telegram команды

Посмотреть текущие алерты:

```text
/alerts