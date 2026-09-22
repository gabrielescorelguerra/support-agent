from typing import Protocol


class TextProcessor(Protocol):
    """Aplica uma transformação determinística a um conteúdo textual."""

    def process(self, text: str) -> str:
        ...
