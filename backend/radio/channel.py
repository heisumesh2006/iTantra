import time
from uuid import UUID
import numpy as np
from scipy.special import erfc
from app.core.errors import ApplicationError
from app.schemas.requests import ChannelConfig
from radio.modulation import modulate, demodulate
from radio.packets import Packet, segment, reassemble


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


def transport(
    payload: bytes, session: UUID, mode: str, language: str, config: ChannelConfig, cancelled=lambda: False
) -> dict:
    start = time.perf_counter()
    packets = segment(payload, session, mode, language, config.packet_size)
    rng = np.random.default_rng(config.seed)
    intact, rows, constellation = [], [], []
    errors = compared = sent_bits = symbols_count = frame_bits = 0
    for packet in packets:
        if cancelled():
            raise ApplicationError("Transmission cancelled", "cancelled", 409)
        source = np.unpackbits(np.frombuffer(packet.serialize(), dtype=np.uint8))
        coded = np.repeat(source, config.repetition)
        symbols, padding = modulate(coded, config.modulation)
        sent_bits += len(coded) + padding
        frame_bits += len(source)
        symbols_count += len(symbols)
        if rng.random() < config.erasure_rate:
            rows.append({"sequence": packet.sequence, "status": "erased", "bit_errors": None})
            continue
        raw_symbols, equalized = apply_channel(symbols, config.channel, config.snr_db, rng)
        received = demodulate(equalized, config.modulation, padding)
        if config.bit_flip_rate:
            received ^= (rng.random(len(received)) < config.bit_flip_rate).astype(np.uint8)
        bit_errors = int(np.count_nonzero(coded != received))
        errors += bit_errors
        compared += len(coded)
        if len(constellation) < 256:
            for raw, eq in zip(
                raw_symbols[: 256 - len(constellation)], equalized[: 256 - len(constellation)]
            ):
                constellation.append(
                    {
                        "i": float(raw.real),
                        "q": float(raw.imag),
                        "equalized_i": float(eq.real),
                        "equalized_q": float(eq.imag),
                    }
                )
        decoded = (
            received
            if config.repetition == 1
            else (received.reshape(-1, 3).sum(axis=1) >= 2).astype(np.uint8)
        )
        try:
            recovered = Packet.parse(np.packbits(decoded).tobytes())
            if (
                recovered.session,
                recovered.sequence,
                recovered.total,
                recovered.mode,
                recovered.language,
            ) != (packet.session, packet.sequence, packet.total, packet.mode, packet.language):
                raise ApplicationError("Recovered header disagrees with current session")
            intact.append(recovered)
            status = "delivered"
        except ApplicationError:
            status = "crc_failed"
        rows.append({"sequence": packet.sequence, "status": status, "bit_errors": bit_errors})
    try:
        recovered_payload = reassemble(intact)
        failure = None
    except ApplicationError as error:
        recovered_payload, failure = None, error.message
    elapsed = (time.perf_counter() - start) * 1000
    return {
        "payload": recovered_payload,
        "failure": failure,
        "packets": rows,
        "constellation": constellation,
        "metrics": {
            "payload_bits": len(payload) * 8,
            "framed_bits": frame_bits,
            "framing_overhead_bits": frame_bits - len(payload) * 8,
            "total_transmitted_bits": sent_bits,
            "recovered_bits": sum(len(p.payload) * 8 for p in intact),
            "raw_ber": errors / compared if compared else None,
            "compared_bits": compared,
            "bit_errors": errors,
            "packet_error_rate": 1 - len(intact) / len(packets),
            "packet_delivery_rate": len(intact) / len(packets),
            "packet_count": len(packets),
            "payload_recovery_rate": float(recovered_payload is not None),
            "channel_ms": elapsed,
            "symbols": symbols_count,
            "simulated_link_seconds": symbols_count / config.symbol_rate,
            "configured_symbol_rate": config.symbol_rate,
            "gross_link_bps": sent_bits / (symbols_count / config.symbol_rate),
        },
    }


def sweep(request) -> dict:
    rng = np.random.default_rng(request.config.seed)
    payload = rng.bytes(1024)
    points, constellation = [], []
    for snr in request.snr_values:
        if not np.isfinite(snr) or not -15 <= snr <= 40:
            raise ApplicationError("Sweep Es/N0 values must be finite and in [-15,40]")
        bit_errors = compared = packet_errors = packet_count = success = 0
        for trial in range(request.trials):
            config = request.config.model_copy(
                update={"snr_db": snr, "seed": (request.config.seed + trial) % 2**32}
            )
            result = transport(payload, UUID(int=1), "semantic", "en", config)
            metrics = result["metrics"]
            bit_errors += metrics["bit_errors"]
            compared += metrics["compared_bits"]
            packet_count += metrics["packet_count"]
            packet_errors += sum(p["status"] != "delivered" for p in result["packets"])
            success += result["payload"] is not None
            constellation = result["constellation"]
        bps = 1 if request.config.modulation == "BPSK" else 2
        reference = (
            float(0.5 * erfc(np.sqrt(10 ** (snr / 10) / bps)))
            if (
                request.config.channel == "awgn"
                and request.config.bit_flip_rate == 0
                and request.config.repetition == 1
            )
            else None
        )
        points.append(
            {
                "snr_db": snr,
                "ber": bit_errors / compared if compared else None,
                "packet_error_rate": packet_errors / packet_count,
                "recovery_rate": success / request.trials,
                "theoretical_ber": reference,
                "compared_bits": compared,
            }
        )
    return {
        "points": points,
        "constellation": constellation,
        "config": request.model_dump(),
        "snr_definition": "Es/N0 dB; unit average symbol energy, coherent perfect CSI for Rayleigh",
    }
