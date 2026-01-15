import unicodedata


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
