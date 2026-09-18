# simula um webhook do Tiflux para testes locais, sem precisar de um servidor externo

import httpx
from uuid import NAMESPACE_URL, uuid5

from telegram import Update
from telegram.ext import ContextTypes

from ia_suporte.schemas.tiflux import TifluxPayload


class TifluxWebhookSimulator:
    # comecar com start
    def __init__(self, simulate_url: str, base_url: str):
        self.simulate_url = simulate_url
        self.base_url = base_url # URL base do servidor FastAPI local

    # simula o envio de um webhook do Tiflux para o bot
    # recebe a mensagem do Telegram, transforma em payload do TiFlux e envia para o endpoint do bot
    async def post(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        message = update.message
        message_text = message.text if message else None

        # comando para resetar o estado do bot, porque nao eh um estado a ser gerido pelo roteador
        if message_text and message_text.lower().startswith("reset"):
            # context.user_data.clear()
            # await message.reply_text("O estado do bot foi reiniciado.")
            return

        # envia o payload simulado para o endpoint do bot
        simulate_tiflux_payload = TifluxPayload(
            message=message_text,
            conversation_id=uuid5(
                NAMESPACE_URL,
                f"telegram:conversation:{message.chat_id}",
            ),
            client_id=str(message.chat_id),
            client_name=(
                message.from_user.first_name
                if message and message.from_user
                else "Cliente"
            ),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{self.simulate_url}",
                json=simulate_tiflux_payload.model_dump(mode="json"),
            )

        response.raise_for_status()
        return response.json()