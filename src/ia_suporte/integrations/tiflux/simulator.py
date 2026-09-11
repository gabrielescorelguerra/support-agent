# simula um webhook do Tiflux para testes locais, sem precisar de um servidor externo

from telegram import Update
from telegram.ext import ContextTypes

from ia_suporte.schemas.tiflux import TifluxPayload
from ia_suporte.orchestration.router import router

class TifluxWebhookSimulator:
    # comecar com start
    def __init__(self, simulate_url: str):
        self.simulate_url = simulate_url

    async def post(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        message = update.message
        message_text = message.text if message else None

        # comando para resetar o estado do bot
        if message_text and message_text.lower().startswith("reset"):
            # context.user_data.clear()
            # await message.reply_text("O estado do bot foi reiniciado.")
            return

        simulate_tiflux_payload = TifluxPayload(
            message=message_text,
        )

        response = await router(simulate_tiflux_payload, self.simulate_url)
        return response