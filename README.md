# Crypto Alerts API

Backend API для работы с криптовалютными ценовыми алертами.

Проект создан на FastAPI и использует PostgreSQL для хранения данных.
Также реализовано получение рыночных данных с Bybit API.

## Возможности

- Получение данных криптовалюты с Bybit
- Spot и USDT Perpetual рынки
- Создание ценовых алертов
- Получение списка алертов
- Получение алерта по ID
- Частичное изменение алерта
- Удаление алерта
- Валидация входных данных
- Хранение данных в PostgreSQL
- Автоматическая документация Swagger

## Стек

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Psycopg
- HTTPX
- Uvicorn

## API

### Получить информацию о монете

```text
GET /coin/{symbol}