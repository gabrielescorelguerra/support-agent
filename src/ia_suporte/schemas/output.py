from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    extra_params: dict[str, str] = Field(default_factory=dict)


class TifluxResponse(BaseModel):
    action: str = "send-message-whatsapp"
    chat_id: int
    contact_info: ContactInfo
