from abc import ABC, abstractmethod


class SpeechRecognitionProvider(ABC):
    @abstractmethod
    def transcribe(self, audio, sample_rate: int, language: str) -> dict: ...


class SpeechSynthesisProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, language: str): ...
