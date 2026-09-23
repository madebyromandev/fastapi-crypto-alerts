from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from services.telegram_commands import telegram_command_worker
from services.alert_worker import alert_worker

from routers import alerts, coins

@asynccontextmanager
async def lifespan(app: FastAPI):
    alert_task = asyncio.create_task(alert_worker())
    telegram_task = asyncio.create_task(
        telegram_command_worker()
    )

    try:
        yield
    finally:
        alert_task.cancel()
        telegram_task.cancel()

        for task in (alert_task, telegram_task):
            try:
                await task
            except asyncio.CancelledError:
                pass

app = FastAPI(
    title="Crypto Alerts API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(alerts.router)
app.include_router(coins.router)


@app.get("/")
def root():
    return {
        "message": "FastAPI работает!"
    }