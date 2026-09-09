from pydantic import BaseModel


class SupportAnalysis(BaseModel):
    situation: str
    next_action: str
    confidence: int