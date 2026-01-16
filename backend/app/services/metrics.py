import unicodedata
import numpy as np


def distance(a, b) -> int:
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]


def text_scores(reference: str | None, hypothesis: str | None):
    if not reference or hypothesis is None:
        return {"wer": None, "cer": None}
    a, b = [unicodedata.normalize("NFC", t).strip() for t in (reference, hypothesis)]
    return {
        "wer": distance(a.split(), b.split()) / len(a.split()) if a.split() else None,
        "cer": distance(a, b) / len(a) if a else None,
    }


def si_sdr(reference, estimate):
    length = min(len(reference), len(estimate))
    x = np.asarray(reference[:length], dtype=np.float64)
    y = np.asarray(estimate[:length], dtype=np.float64)
    x, y = x - x.mean(), y - y.mean()
    energy = np.dot(x, x)
    if energy < 1e-10 or np.dot(y, y) < 1e-10:
        return None
    target = np.dot(x, y) / energy * x
    return float(10 * np.log10((np.dot(target, target) + 1e-12) / (np.dot(y - target, y - target) + 1e-12)))
