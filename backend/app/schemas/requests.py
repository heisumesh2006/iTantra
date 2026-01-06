from typing import Literal, Annotated
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
