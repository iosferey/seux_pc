from fastapi import FastAPI
from pydantic import BaseModel
import os

from seuxpc.modules.pipeline.engine import SEUXPC

app = FastAPI()


class RequestModel(BaseModel):
    url: str
    country: str = "MX"


@app.get("/")
def root():
    return {"status": "SEUX-PC API running"}


@app.post("/analyze")
def analyze(data: RequestModel):

    api_key = os.getenv("OPENAI_API_KEY")

    model = SEUXPC(
        url=data.url,
        target_country=data.country,
        api_key=api_key
    )

    result = model.run()

    return result