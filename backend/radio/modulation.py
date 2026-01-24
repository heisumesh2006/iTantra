import numpy as np
from numpy.typing import NDArray


def modulate(bits: NDArray, modulation: str) -> tuple[NDArray, int]:
    bits = np.asarray(bits, dtype=np.uint8)
    if bits.ndim != 1 or not np.isin(bits, [0, 1]).all():
        raise ValueError("Bits must be a binary vector")
    if modulation == "BPSK":
        return (1.0 - 2.0 * bits).astype(np.complex128), 0
    if modulation == "QPSK":
        padding = len(bits) % 2
        pairs = np.pad(bits, (0, padding)).reshape(-1, 2)
        return ((1.0 - 2.0 * pairs[:, 0]) + 1j * (1.0 - 2.0 * pairs[:, 1])) / np.sqrt(2), padding
    raise ValueError("Unsupported modulation")


def demodulate(symbols: NDArray, modulation: str, padding: int = 0) -> NDArray:
    if modulation == "BPSK":
        return (np.real(symbols) < 0).astype(np.uint8)
    raise ValueError("Unsupported modulation")
