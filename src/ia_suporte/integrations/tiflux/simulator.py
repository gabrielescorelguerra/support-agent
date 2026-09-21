# simula um webhook do Tiflux para testes locais, sem precisar de um servidor externo

import httpx
from uuid import NAMESPACE_URL, uuid5

from telegram import Update
from telegram.ext import ContextTypes

from ia_suporte.messaging.base import MessageSender
from ia_suporte.schemas.tiflux import TifluxPayload


class TifluxWebhookSimulator:
    # comecar com start
    def __init__(
        self,
        simulate_url: str,
        base_url: str,
        message_sender: MessageSender,
    ):
        self.simulate_url = simulate_url
        self.base_url = base_url # URL base do servidor FastAPI local
        self.message_sender = message_sender

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
            # zera o historico
            print("seria resetado o estado do bot")
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

        # chama o endpoint dos agentes de IA para processar a mensagem e gerar a resposta
        # timeout longo por causa do gemini gratis
        timeout = httpx.Timeout(120.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}{self.simulate_url}",
                json=simulate_tiflux_payload.model_dump(mode="json"),
            )

        response.raise_for_status()

        response_data = response.json()
        print(f"Resposta do bot: {response_data}")

        await self.message_sender.send_message(
            recipient_id=str(message.chat_id),
            text=response_data["response"],
        )

        return response_data