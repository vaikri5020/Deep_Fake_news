# News Summarizer & Fake News Detector

A two-model NLP system built with PyTorch. Paste a news article and get:

1. **A FAKE / REAL label** with a confidence score, from a Bidirectional LSTM classifier.
2. **A short summary**, from an LSTM sequence-to-sequence model with attention.

Both models run on the same input text, and a FastAPI backend serves the results to a Gradio web UI.

> **Note:** This system checks writing style, not facts. The fake news model learns patterns from labelled articles. It cannot verify whether a claim is true.

---

## Architecture

```
Browser ──POST /analyze──>  FastAPI backend
                                              │
                                              ▼
                                        src/pipeline.py
                                        ├── predict_fake()  → BiLSTM classifier
                                        └── summarize()     → LSTM seq2seq + attention
                                              │
                                              ▼
                                  { label, confidence, summary }
```

- **Training runs offline** (Google Colab, T4 GPU).
- **Inference runs locally** (CPU is enough).

---

## How the two models work together

The pipeline (`src/pipeline.py`) exposes one function, `analyze(text)`:

1. The text is cleaned and tokenized.
2. **Fake news model:** a BiLSTM reads the article and outputs the probability that it is real. The label is `REAL` if that probability is at least 0.5, otherwise `FAKE`. The confidence is the probability of the predicted label.
3. **Summarizer:** an encoder-decoder LSTM with attention reads the same article and generates a summary token by token.
4. Both results are returned together as one JSON object.

The two models are independent. Neither one uses the other's output, so either can be retrained or replaced without touching the other. Both are loaded once at server startup and cached.

---

## Models

| Component | Architecture | Input | Output | Training data |
|---|---|---|---|---|
| Fake news classifier | Embedding → BiLSTM (128 hidden) → Linear | Article text (max 300 tokens) | FAKE / REAL | Kaggle "Fake and Real News" (Fake.csv, True.csv) |
| Summarizer | Bi-LSTM encoder → LSTM decoder with attention | Article text (max 150 tokens) | Summary (max 50 tokens) | CNN/DailyMail 3.0.0 (subset) |

---

## Project structure

```
news_project/
├── backend/
│   ├── __init__.py
│   └── main.py              # FastAPI app, /analyze and /health
├── frontend/
│   └── app.py               # Gradio UI
├── src/
│   ├── data_loader.py       # downloads Kaggle and Hugging Face datasets
│   ├── preprocess.py        # cleaning, splits, vocabulary
│   ├── nlp_utils.py         # tokenizer and Vocab class (shared)
│   ├── lstm_fake.py         # fake news BiLSTM training and model
│   ├── lstm_summarizer.py   # seq2seq summarizer training and model
│   └── pipeline.py          # combines both models
├── models/                  # trained weights and vocab (not in Git)
├── data/                    # datasets and processed CSVs (not in Git)
├── requirements.txt
└── .gitignore
```

---

## Setup

```bash
git clone <your-repo-url>
cd news_project
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### Model files

The trained weights are not stored in this repository because of their size. Download them from [FILL: Google Drive / Hugging Face link] and place them in `models/`:

- `fake_bilstm.pt`
- `fake_vocab.pkl`
- `summ_lstm_fresh.pt`
- `summ_vocab.pkl`

---

## Usage

### 1. Start the backend

```bash
uvicorn backend.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### 2. Start the frontend

In a second terminal:

```bash
python frontend/app.py
```

Open the URL shown in the terminal (usually http://127.0.0.1:7860).

### API example

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your news article text here, at least 50 characters..."}'
```

Response:

```json
{
  "label": "REAL",
  "confidence": 0.911,
  "summary": "..."
}
```

---

## Training (optional, for reproducing the models)

Run in this order from the project root:

```bash
python -m src.data_loader     # check datasets load
python -m src.preprocess      # clean, split, build vocabularies
python -m src.lstm_fake       # train fake news classifier
python -m src.lstm_summarizer # train summarizer
```

---

## Limitations

- **Fake news detection is style-based.** It can be fooled by well-written false articles and may flag real articles that look unusual. It does not check facts.
- **Dataset bias.** In the Kaggle dataset, real articles come mostly from Reuters and fake ones from other sites. The model may learn source style instead of content. Accuracy on new sources will likely be lower.
- **Summary quality is limited.** The summarizer is a small LSTM trained on a subset of data. Expect generic or incomplete summaries. Pretrained models like BART would perform better.
- **Vocabulary limit.** Words outside the top 20,000 are mapped to `<unk>` and removed from the output.

---

## Future work

- Train the summarizer on the full CNN/DailyMail data for more epochs.
- Evaluate summaries with ROUGE-1, ROUGE-2 and ROUGE-L.
- Compare against a TF-IDF + Logistic Regression baseline.
- Add a dropout layer and beam search to improve summary quality.

---

## Tech stack

Python, PyTorch, scikit-learn, pandas, FastAPI, Uvicorn,  `datasets`, kagglehub.
