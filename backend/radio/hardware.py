from abc import ABC, abstractmethod
from app.core.errors import ApplicationError


class RadioHardwareAdapter(ABC):
    """Future physical-radio boundary. No device is attached or validated by this project."""

    @abstractmethod
    def transmit_receive(self, symbols, sample_rate: int): ...


class UnavailableHardwareAdapter(RadioHardwareAdapter):
    def transmit_receive(self, symbols, sample_rate: int):
        raise ApplicationError(
            "Physical SDR operation is unavailable; use the validated software simulator",
            "hardware_unavailable",
            503,
        )
