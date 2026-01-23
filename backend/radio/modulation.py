import numpy as np
from numpy.typing import NDArray


def modulate(bits: NDArray, modulation: str) -> tuple[NDArray, int]:
    bits = np.asarray(bits, dtype=np.uint8)
    if bits.ndim != 1 or not np.isin(bits, [0, 1]).all():
        raise ValueError("Bits must be a binary vector")
    if modulation == "BPSK":
        return (1.0 - 2.0 * bits).astype(np.complex128), 0
    raise ValueError("Unsupported modulation")
