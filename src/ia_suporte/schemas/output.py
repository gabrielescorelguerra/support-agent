from uuid import UUID

from pydantic import BaseModel, Field


class TifluxResponse(BaseModel):
    action: str = "send_message"
    conversation_id: UUID
    client_id: str
    response: str
    department: str
    metadata: dict[str, object] = Field(default_factory=dict)
