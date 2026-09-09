from pydantic import BaseModel

# webhook TiFlux:
# {
#     "action": "save-contact",
#     "chat_id": 123456,
#     "contact_info": {
#         "name": "Nome do Contato",
#         "email": "email@exemplo.com",
#         "extra_params": {"param1": "valor1"},
#     },
# }


class ContactInfo(BaseModel):
    name: str
    email: str
    extra_params: dict


class AgentResponse(BaseModel):
    action: str
    chat_id: int
    response: str
    contact_info: ContactInfo


class WebhookData(BaseModel):
    chat_id: int
    name: str
    email: str
    messages: list
