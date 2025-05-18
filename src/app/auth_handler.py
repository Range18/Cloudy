import uvicorn
from fastapi import FastAPI

from src.app.yandex.yandex_disk_api_service import YandexDiskApiService

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/auth")
def auth(code: str | None):
    print(code)
    cloud = YandexDiskApiService()
    cloud.authenticate(code)
    return code

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)
