"""Idealized analog latent-channel research. No digital bitstream or low-bitrate claim."""

import numpy as np
from scipy.signal import stft


def log_mel_patches(audio, rate: int):
    _, _, spectrum = stft(audio, rate, nperseg=512, noverlap=352)
    hz = np.linspace(0, rate / 2, 257)
    low = 2595 * np.log10(1 + 80 / 700)
    high = 2595 * np.log10(1 + (rate / 2) / 700)
    edges = 700 * (10 ** (np.linspace(low, high, 42) / 2595) - 1)
    filters = np.maximum(
        0,
        np.minimum(
            (hz[None, :] - edges[:-2, None]) / (edges[1:-1, None] - edges[:-2, None]),
            (edges[2:, None] - hz[None, :]) / (edges[2:, None] - edges[1:-1, None]),
        ),
    )
    mel = np.log(np.maximum(filters @ abs(spectrum) ** 2, 1e-8)).astype(np.float32)
    return np.stack([mel[:, i : i + 32].reshape(-1) for i in range(0, mel.shape[1] - 31, 16)])
