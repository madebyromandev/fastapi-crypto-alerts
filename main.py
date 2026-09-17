from fastapi import FastAPI

from routers import alerts, coins


app = FastAPI(
    title="Crypto Alerts API",
    version="1.0.0"
)

app.include_router(alerts.router)
app.include_router(coins.router)


@app.get("/")
def root():
    return {
        "message": "FastAPI работает!"
    }