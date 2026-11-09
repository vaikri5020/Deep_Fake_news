import torch
import joblib

from src.nlp_utils import tokenize
from src.lstm_fake import FakeBiLSTM, MODEL_PATH as FAKE_MODEL_PATH, VOCAB_PATH as FAKE_VOCAB_PATH, MAX_LEN, DEVICE
from src.lstm_summarizer import summarize as summarize_lstm
from src.groq_summarizer import summarize_groq

_fake_cache = {}


def load_fake():
    if "model" not in _fake_cache:
        vocab = joblib.load(FAKE_VOCAB_PATH)
        model = FakeBiLSTM(len(vocab)).to(DEVICE)
        model.load_state_dict(torch.load(FAKE_MODEL_PATH, map_location=DEVICE))
        model.eval()
        _fake_cache["model"], _fake_cache["vocab"] = model, vocab
    return _fake_cache["model"], _fake_cache["vocab"]


@torch.no_grad()
def predict_fake(text):
    model, vocab = load_fake()
    x = torch.tensor([vocab.encode(tokenize(text), MAX_LEN)]).to(DEVICE)
    p_real = torch.sigmoid(model(x)).item()
    label = "REAL" if p_real >= 0.5 else "FAKE"
    conf = p_real if label == "REAL" else 1 - p_real
    return {"label": label, "confidence": round(conf, 3)}


def get_summary(text, method="groq"):
    if method == "lstm":
        return summarize_lstm(text), "lstm"
    try:
        return summarize_groq(text), "groq"
    except Exception as e:
        print(f"Groq failed, using LSTM fallback: {e}")
        return summarize_lstm(text), "lstm (fallback)"


def analyze(article_text, method="groq"):
    if not article_text or len(article_text.strip()) < 50:
        return {"error": "Article is too short. Give at least 50 characters."}
    fake_result = predict_fake(article_text)
    summary, used = get_summary(article_text, method=method)
    return {
        "label": fake_result["label"],
        "confidence": fake_result["confidence"],
        "summary": summary,
        "summarizer": used,
    }