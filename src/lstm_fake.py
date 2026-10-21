import os
import joblib
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, confusion_matrix

from src.nlp_utils import tokenize, PAD

PROC_DIR = os.path.join("data", "processed")
MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "fake_bilstm.pt")
VOCAB_PATH = os.path.join(MODELS_DIR, "fake_vocab.pkl")
MAX_LEN = 120
EPOCHS = 4
BATCH = 128
LR = 1e-3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class FakeBiLSTM(nn.Module):
    def __init__(self, vocab_size, emb_dim=128, hidden=128, dropout=0.3):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.lstm = nn.LSTM(emb_dim, hidden, batch_first=True, bidirectional=True)
        self.drop = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden * 2, 1)

    def forward(self, x):
        lengths = (x != PAD).sum(1).clamp(min=1).cpu()
        e = self.drop(self.emb(x))
        packed = nn.utils.rnn.pack_padded_sequence(
            e, lengths, batch_first=True, enforce_sorted=False)
        _, (h, _) = self.lstm(packed)
        h = torch.cat([h[0], h[1]], dim=1)
        return self.fc(self.drop(h)).squeeze(-1)


class TextDS(Dataset):
    def __init__(self, texts, labels, vocab):
        self.x = [vocab.encode(tokenize(t), MAX_LEN) for t in texts]
        self.y = labels

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return torch.tensor(self.x[i]), torch.tensor(self.y[i], dtype=torch.float32)


@torch.no_grad()
def predict_probs(model, loader):
    model.eval()
    probs = []
    for xb, _ in loader:
        probs.append(torch.sigmoid(model(xb.to(DEVICE))).cpu())
    return torch.cat(probs).numpy()


def train():
    os.makedirs(MODELS_DIR, exist_ok=True)

    train_df = pd.read_csv(os.path.join(PROC_DIR, "fake_train.csv"))
    val_df = pd.read_csv(os.path.join(PROC_DIR, "fake_val.csv"))
    test_df = pd.read_csv(os.path.join(PROC_DIR, "fake_test.csv"))
    vocab = joblib.load(VOCAB_PATH)

    train_loader = DataLoader(
        TextDS(train_df["text"].tolist(), train_df["label"].values, vocab),
        batch_size=BATCH, shuffle=True)
    val_loader = DataLoader(
        TextDS(val_df["text"].tolist(), val_df["label"].values, vocab),
        batch_size=BATCH)
    test_loader = DataLoader(
        TextDS(test_df["text"].tolist(), test_df["label"].values, vocab),
        batch_size=BATCH)

    model = FakeBiLSTM(len(vocab)).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.BCEWithLogitsLoss()

    best_val = float("inf")
    best_state = None
    for epoch in range(EPOCHS):
        model.train()
        total = 0.0
        for i, (xb, yb) in enumerate(train_loader):
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item()
            if i % 100 == 0:
                print(f"  batch {i}/{len(train_loader)}", flush=True)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                val_loss += loss_fn(model(xb), yb).item()
        val_loss /= len(val_loader)

        print(f"Epoch {epoch+1}/{EPOCHS}  train_loss: {total/len(train_loader):.4f}  "
              f"val_loss: {val_loss:.4f}", flush=True)

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)

    probs = predict_probs(model, test_loader)
    pred = (probs >= 0.5).astype(int)
    y_test = test_df["label"].values
    print(classification_report(y_test, pred, target_names=["FAKE", "REAL"]))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, pred))

    torch.save(model.state_dict(), MODEL_PATH)
    print("Saved:", MODEL_PATH)


if __name__ == "__main__":
    train()