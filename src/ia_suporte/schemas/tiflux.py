from uuid import UUID

from pydantic import BaseModel

class TifluxPayload(BaseModel):
    message: str
    conversation_id: UUID
    message_id: UUID | None = None
    client_id: str
    client_name: str = "Cliente"
    client_email: str = ""