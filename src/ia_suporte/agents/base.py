from uuid import UUID

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Representa o contexto de execução de um agente, incluindo informações sobre a conversa e o histórico de mensagens."""
    conversation_id: UUID
    client_id: str
    history: list[str] = Field(default_factory=list)
    original_history: list[str] = Field(default_factory=list)
    original_message: str = ""
    processed_message: str = ""
    system: str = ""
    product: str = ""
    department: str = ""
    status: str = "IN_PROGRESS"


class AgentResult(BaseModel):
    """Representa o resultado da execução de um agente, incluindo a resposta gerada e informações adicionais."""
    response: str
    department: str
    status: str = "IN_PROGRESS"
    metadata: dict[str, object] = Field(default_factory=dict)
