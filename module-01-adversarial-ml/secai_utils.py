"""
secai_utils.py — small helper module shared by the SecAI adversarial-ML notebooks.

Keeps boilerplate (data loading, tiny models, train/eval loops, plotting) out of the
notebooks so the lecture can focus on the attacks and defenses themselves.
"""
import os
import io
import csv
import gzip
import time
import urllib.request

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_everything(seed: int = 0):
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ----------------------------------------------------------------------------
# MNIST (raw IDX files; tries several mirrors so it works behind most firewalls)
# ----------------------------------------------------------------------------
_MIRRORS = {
    "mnist": [
        "https://ossci-datasets.s3.amazonaws.com/mnist/",
        "https://raw.githubusercontent.com/fgnt/mnist/master/",
        "http://yann.lecun.com/exdb/mnist/",
    ],
    "fashion": [
        "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/",
        "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/",
    ],
}
FASHION_CLASSES = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]
_MNIST_FILES = {
    "train_x": "train-images-idx3-ubyte.gz",
    "train_y": "train-labels-idx1-ubyte.gz",
    "test_x": "t10k-images-idx3-ubyte.gz",
    "test_y": "t10k-labels-idx1-ubyte.gz",
}


def _download(fname: str, dataset: str = "mnist") -> str:
    path = os.path.join(DATA_DIR, f"{dataset}_{fname}")
    if os.path.exists(path):
        return path
    last_err = None
    for base in _MIRRORS[dataset]:
        try:
            print(f"Downloading {fname} from {base} ...")
            urllib.request.urlretrieve(base + fname, path)
            return path
        except Exception as e:  # noqa: BLE001
            last_err = e
            if os.path.exists(path):
                os.remove(path)
    raise RuntimeError(f"Could not download {fname}: {last_err}")


def _read_idx(path: str) -> np.ndarray:
    with gzip.open(path, "rb") as f:
        data = f.read()
    magic = int.from_bytes(data[0:4], "big")
    ndim = magic & 0xFF
    shape = [int.from_bytes(data[4 + 4 * i: 8 + 4 * i], "big") for i in range(ndim)]
    return np.frombuffer(data, dtype=np.uint8, offset=4 + 4 * ndim).reshape(shape)


def load_mnist(n_train: int | None = None, n_test: int | None = None, seed: int = 0, dataset: str = "mnist"):
    """Return (x_train, y_train, x_test, y_test) as float tensors in [0, 1], shape (N, 1, 28, 28).

    `dataset` is "mnist" (digits) or "fashion" (Fashion-MNIST: same format, harder task).
    Pixels are kept in [0, 1] (no mean/std normalisation) so that an L-inf budget `eps`
    has an obvious meaning: eps = 0.1 means "each pixel may move by at most 10% of its range".
    """
    xs = _read_idx(_download(_MNIST_FILES["train_x"], dataset)).astype(np.float32) / 255.0
    ys = _read_idx(_download(_MNIST_FILES["train_y"], dataset)).astype(np.int64)
    xt = _read_idx(_download(_MNIST_FILES["test_x"], dataset)).astype(np.float32) / 255.0
    yt = _read_idx(_download(_MNIST_FILES["test_y"], dataset)).astype(np.int64)

    rng = np.random.default_rng(seed)
    if n_train is not None:
        idx = rng.choice(len(xs), n_train, replace=False)
        xs, ys = xs[idx], ys[idx]
    if n_test is not None:
        idx = rng.choice(len(xt), n_test, replace=False)
        xt, yt = xt[idx], yt[idx]

    to_t = lambda a: torch.from_numpy(np.ascontiguousarray(a))
    return (to_t(xs).unsqueeze(1), to_t(ys), to_t(xt).unsqueeze(1), to_t(yt))


def load_fashion_mnist(n_train: int | None = None, n_test: int | None = None, seed: int = 0):
    return load_mnist(n_train, n_test, seed, dataset="fashion")


# ----------------------------------------------------------------------------
# SST-2 (binary sentiment, short movie-review sentences)
# ----------------------------------------------------------------------------
_SST2_BASE = "https://raw.githubusercontent.com/clairett/pytorch-sentiment-classification/master/data/SST2/"


def load_sst2():
    """Return (train_texts, train_labels, test_texts, test_labels). Labels: 1 = positive, 0 = negative."""
    out = []
    for split in ("train", "test"):
        path = os.path.join(DATA_DIR, f"sst2_{split}.tsv")
        if not os.path.exists(path):
            print(f"Downloading SST-2 {split} split ...")
            urllib.request.urlretrieve(_SST2_BASE + f"{split}.tsv", path)
        texts, labels = [], []
        with open(path, encoding="utf-8") as f:
            for row in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if len(row) != 2:
                    continue
                texts.append(row[0].strip())
                labels.append(int(row[1]))
        out += [texts, np.array(labels)]
    return tuple(out)


# ----------------------------------------------------------------------------
# Tiny models
# ----------------------------------------------------------------------------
class SmallCNN(nn.Module):
    """Classic 2-conv MNIST network (~99% test accuracy after 1-2 epochs)."""

    def __init__(self, n_classes: int = 10, width: int = 32):
        super().__init__()
        self.conv1 = nn.Conv2d(1, width, 3, padding=1)
        self.conv2 = nn.Conv2d(width, 2 * width, 3, padding=1)
        self.fc1 = nn.Linear(2 * width * 7 * 7, 128)
        self.fc2 = nn.Linear(128, n_classes)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)), 2)
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = x.flatten(1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


class MLP(nn.Module):
    """Fully-connected baseline — a *different architecture* for transferability experiments."""

    def __init__(self, n_classes: int = 10, hidden: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28 * 28, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, n_classes),
        )

    def forward(self, x):
        return self.net(x)


# ----------------------------------------------------------------------------
# Training / evaluation helpers
# ----------------------------------------------------------------------------
def iterate_minibatches(x, y, batch_size: int, shuffle: bool = True):
    n = len(x)
    idx = torch.randperm(n) if shuffle else torch.arange(n)
    for i in range(0, n, batch_size):
        j = idx[i: i + batch_size]
        yield x[j], y[j]


def train(model, x, y, epochs: int = 1, lr: float = 1e-3, batch_size: int = 128,
          weight_decay: float = 0.0, attack=None, verbose: bool = True):
    """Minimal training loop.

    `attack` (optional) is a callable attack(model, x, y) -> x_adv. When given, the model is
    trained on adversarial examples generated on the fly  ==>  *adversarial training*.
    """
    model.to(DEVICE).train()
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    t0 = time.time()
    for ep in range(epochs):
        tot, correct, loss_sum = 0, 0, 0.0
        for xb, yb in iterate_minibatches(x, y, batch_size):
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            if attack is not None:
                model.eval()
                xb = attack(model, xb, yb).detach()
                model.train()
            logits = model(xb)
            loss = F.cross_entropy(logits, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            loss_sum += loss.item() * len(xb)
            correct += (logits.argmax(1) == yb).sum().item()
            tot += len(xb)
        if verbose:
            print(f"epoch {ep + 1}/{epochs}  loss={loss_sum / tot:.4f}  train_acc={correct / tot:.4f}  ({time.time() - t0:.0f}s)")
    model.eval()
    return model


@torch.no_grad()
def predict(model, x, batch_size: int = 512):
    model.eval()
    outs = []
    for i in range(0, len(x), batch_size):
        outs.append(model(x[i: i + batch_size].to(DEVICE)).cpu())
    return torch.cat(outs)


def accuracy(model, x, y) -> float:
    return (predict(model, x).argmax(1) == y).float().mean().item()


# ----------------------------------------------------------------------------
# Plotting
# ----------------------------------------------------------------------------
def show_images(images, titles=None, n_cols: int = 8, cmap: str = "gray", figsize=None, suptitle=None):
    """images: tensor/array of shape (N, 1, H, W) or (N, H, W)."""
    images = torch.as_tensor(images).detach().cpu()
    if images.ndim == 4:
        images = images[:, 0]
    n = len(images)
    n_rows = int(np.ceil(n / n_cols))
    figsize = figsize or (1.4 * n_cols, 1.6 * n_rows)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes = np.atleast_1d(axes).ravel()
    for i, ax in enumerate(axes):
        ax.axis("off")
        if i < n:
            ax.imshow(images[i], cmap=cmap, vmin=0, vmax=1)
            if titles is not None:
                ax.set_title(str(titles[i]), fontsize=9)
    if suptitle:
        fig.suptitle(suptitle)
    plt.tight_layout()
    plt.show()
