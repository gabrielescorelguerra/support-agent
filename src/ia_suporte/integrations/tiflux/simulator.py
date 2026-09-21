# simula um webhook do Tiflux para testes locais, sem precisar de um servidor externo

import httpx
from uuid import NAMESPACE_URL, uuid5

from telegram import Update
from telegram.ext import ContextTypes

from ia_suporte.messaging.base import MessageSender
from ia_suporte.persistence import ConversationStore
from ia_suporte.schemas.tiflux import TifluxPayload


class TifluxWebhookSimulator:
    # essas variaveis persistem entre as chamadas
    def __init__(
        self,
        simulate_url: str,
        base_url: str,
        message_sender: MessageSender,
        conversation_store: ConversationStore,
    ):
        self.simulate_url = simulate_url
        self.base_url = base_url # URL base do servidor FastAPI local
        self.message_sender = message_sender
        self.conversation_store = conversation_store

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
            conversation_id = uuid5(
                NAMESPACE_URL,
                f"telegram:conversation:{message.chat_id}",
            )
            self.conversation_store.reset_conversation(conversation_id)
            self.simulate_url = "/start"
            print("Histórico resetado e rota reiniciada.")
            return

        # envia o payload simulado para o endpoint do bot
        simulate_tiflux_payload = TifluxPayload(
            message=message_text,
            conversation_id=uuid5(
                NAMESPACE_URL,
                f"telegram:conversation:{message.chat_id}",
            ),
            client_id=str(message.from_user.id) if message and message.from_user else "unknown", 
            client_name=(
                message.from_user.first_name
                if message and message.from_user
                else "Cliente"
            ),
        )

        # url antes de chamar o webhook
        previous_url = self.simulate_url

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

        # atualiza a rota com base no campo personalizado
        route = response_data["contact_info"]["extra_params"]["route"]
        self.simulate_url = f"/webhook/{route}"

        # envia a resposta do bot para o Telegram
        await self.message_sender.send_message(
            recipient_id=str(message.chat_id),
            text=response_data["contact_info"]["extra_params"]["message"],
        )

                # se houver uma mudança de departamento, envia mensagem fixa
        if previous_url != self.simulate_url and route != "triage":
            await self.message_sender.send_message(
                recipient_id=str(message.chat_id),
                text=(
                    "Olá, sou do time de "
                    f"{self._department_name(route)}. Como posso ajudá-lo?"
                ),
            )

        return response_data

    @staticmethod
    def _department_name(route: str) -> str:
        names = {
            "finance": "financeiro",
            "support": "suporte",
            "commercial": "comercial",
            "invoice": "notas fiscais",
            "ad_hoc_support": "atendimento avulso",
            "equipment_maintenance": "manutenção de equipamentos",
            "system_and_customer_data_update":
                "alteração de sistema e atualização cadastral",
            "supplies": "suprimentos",
            "contracts": "contratos",
            "customer_service": "atendimento ao cliente",
            "marketplace_and_complaints":
                "Mercado Livre e Reclame Aqui",
            "cancellation": "cancelamento",
            "human_support": "atendimento",
            "agent_test": "teste do agente",
            "end": "encerramento",
        }
        return names.get(route, route.replace("_", " "))