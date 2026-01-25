

def apply_channel(symbols, kind: str, snr_db: float, rng):
    # Es = 1 for both constellations. Complex noise power N0 = 10^(-Es/N0 dB / 10).
    if kind == "ideal":
        return symbols.copy(), symbols.copy()
    raise ValueError("Unknown channel")
