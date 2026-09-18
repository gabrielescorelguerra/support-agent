from uuid import UUID

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    conversation_id: UUID
    client_id: str
    history: list[str] = Field(default_factory=list)
    system: str = ""
    product: str = ""
    department: str = ""
    status: str = "IN_PROGRESS"


class AgentResult(BaseModel):
    response: str
    department: str
    status: str = "IN_PROGRESS"
    metadata: dict[str, object] = Field(default_factory=dict)
