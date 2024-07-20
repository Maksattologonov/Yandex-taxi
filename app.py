from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="Yandex taxi",
    description="",
    version="1.0.0",
)


app.include_router()