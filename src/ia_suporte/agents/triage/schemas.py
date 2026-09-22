from typing import Literal

from pydantic import BaseModel

SimpleMessageType = Literal[
    "morning_greeting",
    "afternoon_greeting",
    "evening_greeting",
    "well_being",
    "hello",
]


# modelo de resposta da análise de triagem (definição de rota, confiança e dados adicionais)
class TriageAnalysis(BaseModel):
    route: str | None
    confidence: int
    system: str
    product: str
    sentiment: str | None = None
    simple_message_type: SimpleMessageType | None = None
