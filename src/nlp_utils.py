import re
from collections import Counter

PAD, UNK, SOS, EOS = 0, 1, 2, 3


def clean(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\(reuters\)\s*-?", " ", text, flags=re.I)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text):
    return re.findall(r"[a-z0-9']+", clean(text).lower())


class Vocab:
    def __init__(self, token_lists, max_size=20000, min_freq=2):
        counter = Counter(t for toks in token_lists for t in toks)
        self.itos = ["<pad>", "<unk>", "<sos>", "<eos>"]
        for word, cnt in counter.most_common(max_size - 4):
            if cnt >= min_freq:
                self.itos.append(word)
        self.stoi = {w: i for i, w in enumerate(self.itos)}

    def __len__(self):
        return len(self.itos)

    def encode(self, tokens, max_len):
        ids = [self.stoi.get(t, UNK) for t in tokens][:max_len]
        return ids + [PAD] * (max_len - len(ids))

    def decode(self, ids):
        words = []
        for i in ids:
            if i == EOS:
                break
            if i > EOS:
                words.append(self.itos[i])
        return " ".join(words)