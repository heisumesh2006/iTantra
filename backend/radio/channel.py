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
    if kind == "rayleigh":
        # IID flat fading per symbol, E|h|^2 = 1; ideal receiver CSI, coherent equalization.
        h = (rng.normal(size=len(symbols)) + 1j * rng.normal(size=len(symbols))) / np.sqrt(2)
        received = h * symbols + noise
        return received, received / np.where(np.abs(h) < 1e-12, 1e-12, h)
    raise ValueError("Unknown channel")
