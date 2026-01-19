from abc import ABC, abstractmethod


class SpeechRecognitionProvider(ABC):
    @abstractmethod
    def transcribe(self, audio, sample_rate: int, language: str) -> dict: ...
