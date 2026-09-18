from fastapi import FastAPI

from database import init_db

app = FastAPI(
    title="Re:World API",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "reworld"}