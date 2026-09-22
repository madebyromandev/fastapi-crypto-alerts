from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from services.alert_worker import alert_worker

from routers import alerts, coins

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(alert_worker())

    try:
        yield
    finally:
        worker_task.cancel()

        try:
            await worker_task
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