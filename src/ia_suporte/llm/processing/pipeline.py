from ia_suporte.llm.processing.base import TextProcessor
from ia_suporte.llm.processing.processors import (
    NormalizeWhitespace,
    RedactSensitiveData,
)


class TextProcessingPipeline:
    def __init__(self, processors: list[TextProcessor]):
        self.processors = processors

    def process(self, text: str) -> str:
        """Aplica uma sequência de processadores de texto ao conteúdo recebido."""
        for processor in self.processors:
            text = processor.process(text)
        return text


TEXT_PIPELINES = {
    "triage": TextProcessingPipeline(
        processors=[
            NormalizeWhitespace(),
            RedactSensitiveData(),
        ]
    ),
    "support": TextProcessingPipeline(
        processors=[
            NormalizeWhitespace(),
            RedactSensitiveData(),
        ]
    ),
}


def get_text_processing_pipeline(department: str) -> TextProcessingPipeline:
    try:
        return TEXT_PIPELINES[department]
    except KeyError as error:
        raise ValueError(
            f"No text processing pipeline configured for department: {department}"
        ) from error
