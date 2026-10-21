import os
import shutil
import kagglehub
import pandas as pd
from datasets import load_dataset

RAW_DIR = os.path.join("data", "raw")
FAKE_SLUG = "clmentbisaillon/fake-and-real-news-dataset"


def _copy_fake_files():
    """Kaggle se Fake.csv aur True.csv data/raw/ mein copy karta hai."""
    os.makedirs(RAW_DIR, exist_ok=True)
    cache = kagglehub.dataset_download(FAKE_SLUG)
    for f in ["Fake.csv", "True.csv"]:
        dest = os.path.join(RAW_DIR, f)
        if not os.path.exists(dest):
            shutil.copy(os.path.join(cache, f), dest)


def load_fake_news():
    """Fake/Real dataset. Output columns: text, label (0 = FAKE, 1 = REAL)."""
    _copy_fake_files()
    fake = pd.read_csv(os.path.join(RAW_DIR, "Fake.csv"))
    true = pd.read_csv(os.path.join(RAW_DIR, "True.csv"))
    fake["label"] = 0
    true["label"] = 1

    df = pd.concat([fake, true], ignore_index=True)
    df["text"] = df["title"].fillna("") + " " + df["text"].fillna("")
    df = df[df["text"].str.strip().str.len() > 20]
    df = df.drop_duplicates(subset=["text"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df[["text", "label"]]


def load_cnn_summaries(split="train", max_samples=None):
    """CNN/DailyMail. Output columns: article, highlights (human summary)."""
    ds = load_dataset("abisee/cnn_dailymail", "3.0.0", split=split)
    df = ds.to_pandas()[["article", "highlights"]]
    df = df[df["article"].str.len() > 300]
    if max_samples:
        df = df.sample(n=min(max_samples, len(df)), random_state=42)
    return df.reset_index(drop=True)


if __name__ == "__main__":
    fake = load_fake_news()
    print("Fake/Real shape:", fake.shape)
    print(fake["label"].value_counts())

    cnn = load_cnn_summaries("train", max_samples=5)
    print("CNN shape:", cnn.shape)
    print("Article:", cnn.iloc[0]["article"][:200], "...")
    print("Highlights:", cnn.iloc[0]["highlights"])