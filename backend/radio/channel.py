import numpy as np


def apply_channel(symbols, kind: str, snr_db: float, rng):
    # Es = 1 for both constellations. Complex noise power N0 = 10^(-Es/N0 dB / 10).
    if kind == "ideal":
        return symbols.copy(), symbols.copy()
    noise = np.sqrt(10.0 ** (-snr_db / 10.0) / 2) * (
        rng.normal(size=len(symbols)) + 1j * rng.normal(size=len(symbols))
    )
    if kind == "awgn":
        received = symbols + noise
        return received, received
    raise ValueError("Unknown channel")
