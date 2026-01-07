from typing import Literal, Annotated
from uuid import UUID
from pydantic import BaseModel, Field

Snr = Annotated[float, Field(ge=-15, le=40, allow_inf_nan=False)]

Language = Literal["en", "hi", "kn", "ta", "te", "ml"]
Mode = Literal["conventional", "neural", "semantic", "adaptive"]


class ChannelConfig(BaseModel):
    modulation: Literal["BPSK", "QPSK"] = "BPSK"
    channel: Literal["ideal", "awgn", "rayleigh"] = "awgn"
    snr_db: float = Field(default=12, ge=-15, le=40, allow_inf_nan=False)
    packet_size: int = Field(default=256, ge=32, le=1024)
    repetition: Literal[1, 3] = 1
    erasure_rate: float = Field(default=0, ge=0, le=1, allow_inf_nan=False)
    bit_flip_rate: float = Field(default=0, ge=0, le=0.5, allow_inf_nan=False)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    symbol_rate: int = Field(default=12000, ge=100, le=1000000)


class TransmissionRequest(BaseModel):
    media_id: UUID | None = None
    text: str | None = Field(default=None, max_length=4000)
    reference: str | None = Field(default=None, max_length=4000)
    language: Language = "en"
    mode: Mode = "conventional"
    bandwidth_kbps: Literal[1.5, 3.0, 6.0, 12.0] = 3.0
    budget_kbps: float = Field(default=8, ge=0.1, le=256, allow_inf_nan=False)
    objective: Literal["meaning", "waveform"] = "meaning"
    target_latency_ms: int = Field(default=10000, ge=100, le=120000)
    channel_config: ChannelConfig = Field(default_factory=ChannelConfig)


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    language: Language = "en"


class TranscriptionRequest(BaseModel):
    media_id: UUID
    language: Language = "en"


class ChannelSweepRequest(BaseModel):
    config: ChannelConfig = Field(default_factory=ChannelConfig)
    snr_values: list[Snr] = Field(
        default_factory=lambda: [-4, -2, 0, 2, 4, 6, 8, 10, 12], min_length=1, max_length=21
    )
    trials: int = Field(default=24, ge=1, le=100)
