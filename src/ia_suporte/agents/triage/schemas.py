from pydantic import BaseModel


# modelo de resposta da análise de triagem (definição de rota, confiança e dados adicionais)
class TriageAnalysis(BaseModel):
    route: str | None
    confidence: int
    system: str
    product: str
    sentiment: str | None = None
