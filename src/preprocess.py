import os
import re
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data_loader import load_fake_news, load_cnn_summaries
from src.nlp_utils import clean, tokenize, Vocab

PROC_DIR = os.path.join("data", "processed")
MODELS_DIR = "models"
SEED = 42


def clean_cnn(text):
    """CNN/DailyMail text saaf karta hai."""
    if not isinstance(text, str):
        return ""
    text = text.replace("\n", " ")
    text = re.sub(r"^\s*\(CNN\)\s*(--)?\s*", "", text)   # "(CNN) --" prefix hatao
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prepare_fake():
    """Fake/Real news: clean, stratified split (80/10/10), vocab sirf train se."""
    os.makedirs(PROC_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = load_fake_news()
    df["text"] = df["text"].apply(clean)
    df = df[df["text"].str.len() > 50]
    df = df.drop_duplicates(subset=["text"])

    train, temp = train_test_split(
        df, test_size=0.2, stratify=df["label"], random_state=SEED)
    val, test = train_test_split(
        temp, test_size=0.5, stratify=temp["label"], random_state=SEED)

    for name, part in [("train", train), ("val", val), ("test", test)]:
        part.to_csv(os.path.join(PROC_DIR, f"fake_{name}.csv"), index=False)
        print(f"fake_{name}: {len(part)} rows, labels:",
              part["label"].value_counts().to_dict())

    vocab = Vocab([tokenize(t) for t in train["text"]], max_size=20000, min_freq=2)
    joblib.dump(vocab, os.path.join(MODELS_DIR, "fake_vocab.pkl"))
    print("Fake vocab size:", len(vocab))


def prepare_summ(n_train=10000, n_val=1000, n_test=500):
    """CNN/DailyMail: clean, official splits, token length check, vocab sirf train se."""
    os.makedirs(PROC_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    splits = {
        "train": load_cnn_summaries("train", max_samples=n_train),
        "val": load_cnn_summaries("validation", max_samples=n_val),
        "test": load_cnn_summaries("test", max_samples=n_test),
    }

    for name in splits:
        df = splits[name]
        df["article"] = df["article"].apply(clean_cnn)
        df["highlights"] = df["highlights"].apply(clean_cnn)
        df = df[(df["article"].str.len() > 200) & (df["highlights"].str.len() > 20)]
        df = df.reset_index(drop=True)
        splits[name] = df
        df.to_csv(os.path.join(PROC_DIR, f"summ_{name}.csv"), index=False)
        print(f"summ_{name}: {len(df)} rows")

    train = splits["train"]
    art_len = train["article"].apply(lambda t: len(tokenize(t)))
    hl_len = train["highlights"].apply(lambda t: len(tokenize(t)))
    print("Article tokens (50/90/95 percentile):",
          art_len.quantile([0.5, 0.9, 0.95]).tolist())
    print("Highlight tokens (50/90/95 percentile):",
          hl_len.quantile([0.5, 0.9, 0.95]).tolist())

    vocab_texts = train["article"].apply(tokenize).tolist()
    vocab_texts += train["highlights"].apply(tokenize).tolist()
    vocab = Vocab(vocab_texts, max_size=20000, min_freq=2)
    joblib.dump(vocab, os.path.join(MODELS_DIR, "summ_vocab.pkl"))
    print("Summ vocab size:", len(vocab))


if __name__ == "__main__":
    prepare_fake()
    prepare_summ()