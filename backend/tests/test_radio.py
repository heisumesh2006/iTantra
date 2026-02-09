import numpy as np
import pytest
from radio.modulation import modulate, demodulate


@pytest.mark.parametrize("modulation", ["BPSK", "QPSK"])
@pytest.mark.parametrize("size", [1, 7, 8, 10001])
def test_noiseless_modulation(modulation, size):
    bits = np.random.default_rng(7).integers(0, 2, size, dtype=np.uint8)
    symbols, padding = modulate(bits, modulation)
    assert np.allclose(np.abs(symbols), 1)
    np.testing.assert_array_equal(bits, demodulate(symbols, modulation, padding))
