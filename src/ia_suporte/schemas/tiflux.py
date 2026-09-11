from pydantic import BaseModel

class TifluxPayload(BaseModel):
    # token: str                     # Token de autenticação
    # chat_profile: dict             # Perfil do usuário
    # chat_id: int                   # ID do chat em andamento
    message: str                   # Última mensagem enviada pelo usuário no chat
    # organization_id: int           # ID da organização
    # client_name: str               # Nome do contato associado ao chat
    # client_phone: str              # Telefone do contato associado ao chat
    # client_email: str              # E-mail do contato
    # client_company: dict           # Dados da empresa/cliente vinculado ao chat
