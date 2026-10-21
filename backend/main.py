import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to Python's path so "src" can be imported
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.pipeline import analyze, load_fake
from src.lstm_summarizer import load_summarizer


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=50, description="News article text")


class AnalyzeResponse(BaseModel):
    label: str
    confidence: float
    summary: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_fake()
    load_summarizer()
    print("Models loaded, server ready.")
    yield


app = FastAPI(
    title="News Summarizer & Fake News Detector API",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_article(req: AnalyzeRequest):
    result = analyze(req.text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result