import os
import joblib
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from src.nlp_utils import tokenize, PAD, SOS, EOS, UNK

PROC_DIR = os.path.join("data", "processed")
MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "summ_lstm_v2.pt")
VOCAB_PATH = os.path.join(MODELS_DIR, "summ_vocab.pkl")
SRC_LEN = 150       # article ki max length (tokens)
TGT_LEN = 50  
EMB = 128
ENC_HID = 256
DEC_HID = ENC_HID * 2      # highlights ki max length (tokens)
EPOCHS = 15
BATCH = 64
LR = 1e-3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class Encoder(nn.Module):
    def __init__(self, vocab_size, emb=EMB, hid=ENC_HID):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb, padding_idx=PAD)
        self.lstm = nn.LSTM(emb, hid, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hid * 2, hid * 2)

    def forward(self, src):
        lengths = (src != PAD).sum(1).clamp(min=1).cpu()
        packed = nn.utils.rnn.pack_padded_sequence(
            self.emb(src), lengths, batch_first=True, enforce_sorted=False)
        out, (h, _) = self.lstm(packed)
        out, _ = nn.utils.rnn.pad_packed_sequence(
            out, batch_first=True, total_length=src.size(1))
        h_cat = torch.cat([h[0], h[1]], dim=1)
        dec_h0 = torch.tanh(self.fc(h_cat))
        return out, dec_h0


class Decoder(nn.Module):
    def __init__(self, vocab_size, emb=EMB, hid=DEC_HID):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb, padding_idx=PAD)
        self.lstm = nn.LSTM(emb + hid, hid, batch_first=True)
        self.out = nn.Linear(hid * 2, vocab_size)

    def step(self, tok, h, c, enc_out, mask):
        e = self.emb(tok).unsqueeze(1)
        scores = torch.bmm(enc_out, h.unsqueeze(2)).squeeze(2)
        scores = scores.masked_fill(~mask, -1e9)
        attn = torch.softmax(scores, dim=1)
        ctx = torch.bmm(attn.unsqueeze(1), enc_out)
        inp = torch.cat([e, ctx], dim=2)
        out, (h2, c2) = self.lstm(inp, (h.unsqueeze(0), c.unsqueeze(0)))
        h2, c2 = h2.squeeze(0), c2.squeeze(0)
        logits = self.out(torch.cat([h2, ctx.squeeze(1)], dim=1))
        return logits, h2, c2


class Seq2Seq(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.enc = Encoder(vocab_size)
        self.dec = Decoder(vocab_size)

    def forward(self, src, tgt):
        mask = src != PAD
        enc_out, h = self.enc(src)
        c = torch.zeros_like(h)
        outs = []
        for t in range(tgt.size(1) - 1):
            logits, h, c = self.dec.step(tgt[:, t], h, c, enc_out, mask)
            outs.append(logits)
        return torch.stack(outs, dim=1)


class SummDS(Dataset):
    def __init__(self, src_ids, tgt_ids):
        self.src, self.tgt = src_ids, tgt_ids

    def __len__(self):
        return len(self.src)

    def __getitem__(self, i):
        return torch.tensor(self.src[i]), torch.tensor(self.tgt[i])


def encode_target(tokens, vocab):
    ids = [vocab.stoi.get(t, UNK) for t in tokens][:TGT_LEN - 2]
    ids = [SOS] + ids + [EOS]
    return ids + [PAD] * (TGT_LEN - len(ids))


def encode_source(text, vocab):
    return vocab.encode(tokenize(text), SRC_LEN)


def build_ds(df, vocab):
    src_ids = [encode_source(t, vocab) for t in df["article"]]
    tgt_ids = [encode_target(tokenize(t), vocab) for t in df["highlights"]]
    return SummDS(src_ids, tgt_ids)


@torch.no_grad()
def summarize(text, max_out=TGT_LEN, min_out=8):
    model, vocab = load_summarizer()
    src = torch.tensor([encode_source(text, vocab)]).to(DEVICE)
    mask = src != PAD
    enc_out, h = model.enc(src)
    c = torch.zeros_like(h)
    tok = torch.tensor([SOS]).to(DEVICE)
    out_ids = []
    for step in range(max_out):
        logits, h, c = model.dec.step(tok, h, c, enc_out, mask)
        logits[0, EOS] = -1e9 if step < min_out else logits[0, EOS]
        logits[0, UNK] = -1e9
        if out_ids:
            logits[0, out_ids[-1]] = -1e9
        tok = logits.argmax(dim=1)
        if tok.item() == EOS:
            break
        out_ids.append(tok.item())
    return vocab.decode(out_ids)
    
@torch.no_grad()
def eval_loss(model, loader, loss_fn):
    model.eval()
    total = 0.0
    for src, tgt in loader:
        src, tgt = src.to(DEVICE), tgt.to(DEVICE)
        logits = model(src, tgt)
        total += loss_fn(logits.reshape(-1, logits.size(-1)),
                         tgt[:, 1:].reshape(-1)).item()
    return total / len(loader)

def train():
    os.makedirs(MODELS_DIR, exist_ok=True)

    train_df = pd.read_csv(os.path.join(PROC_DIR, "summ_train.csv"))
    val_df = pd.read_csv(os.path.join(PROC_DIR, "summ_val.csv"))
    vocab = joblib.load(VOCAB_PATH)

    train_loader = DataLoader(build_ds(train_df, vocab), batch_size=BATCH, shuffle=True)
    val_loader = DataLoader(build_ds(val_df, vocab), batch_size=BATCH)

    model = Seq2Seq(len(vocab)).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5, patience=1)
    loss_fn = nn.CrossEntropyLoss(ignore_index=PAD)

    best_val, best_state = float("inf"), None
    for epoch in range(EPOCHS):
        model.train()
        total = 0.0
        for i, (src, tgt) in enumerate(train_loader):
            src, tgt = src.to(DEVICE), tgt.to(DEVICE)
            logits = model(src, tgt)
            loss = loss_fn(logits.reshape(-1, logits.size(-1)),
                           tgt[:, 1:].reshape(-1))
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += loss.item()
            if i % 100 == 0:
                print(f"  batch {i}/{len(train_loader)}", flush=True)

        val_loss = eval_loss(model, val_loader, loss_fn)
        scheduler.step(val_loss)
        print(f"Epoch {epoch+1}/{EPOCHS}  train_loss: {total/len(train_loader):.4f}  "
              f"val_loss: {val_loss:.4f}", flush=True)

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    torch.save(model.state_dict(), MODEL_PATH)
    print("Saved:", MODEL_PATH)


_cache = {}


def load_summarizer():
    if "model" not in _cache:
        vocab = joblib.load(VOCAB_PATH)
        model = Seq2Seq(len(vocab)).to(DEVICE)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        _cache["model"], _cache["vocab"] = model, vocab
    return _cache["model"], _cache["vocab"]


@torch.no_grad()
def summarize(text, max_out=TGT_LEN):
    model, vocab = load_summarizer()
    src = torch.tensor([encode_source(text, vocab)]).to(DEVICE)
    mask = src != PAD
    enc_out, h = model.enc(src)
    c = torch.zeros_like(h)
    tok = torch.tensor([SOS]).to(DEVICE)
    out_ids = []
    for _ in range(max_out):
        logits, h, c = model.dec.step(tok, h, c, enc_out, mask)
        tok = logits.argmax(dim=1)
        if tok.item() == EOS:
            break
        out_ids.append(tok.item())
    return vocab.decode(out_ids)


if __name__ == "__main__":
    train()
    sample = pd.read_csv(os.path.join(PROC_DIR, "summ_val.csv")).iloc[0]["article"]
    print("Summary:", summarize(sample))