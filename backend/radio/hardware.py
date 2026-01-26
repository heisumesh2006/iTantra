from abc import ABC, abstractmethod


class RadioHardwareAdapter(ABC):
    """Future physical-radio boundary. No device is attached or validated by this project."""

    @abstractmethod
    def transmit_receive(self, symbols, sample_rate: int): ...
