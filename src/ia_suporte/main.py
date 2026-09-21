# # # EXEMPLO
# # triage_llm = GeminiClient()
# # response_llm = GroqClient()

# # triage_agent = TriageAgent(
# #     triage_llm=triage_llm,
# #     response_llm=response_llm
# # )

# # from .base import LLM

# from ia_suporte.agents.base import WebhookData
# from ia_suporte.agents.triage.agent import TriageAgent
# from ia_suporte.llm.gemini import GeminiLLM

# gemini_2_5_flash = GeminiLLM("gemini-3.1-flash-lite")
# gemini_3_1_flash = GeminiLLM("gemini-3.1-flash")

# data = WebhookData(
#     chat_id=123, name="Roberto", email="a@gmail.com", messages=["oi", "ok"]
# )

# triage_agent = TriageAgent(llm=gemini_2_5_flash, data=data)

# # if for pra triagem
# response = triage_agent.run()
# print(response)

from ia_suporte.integrations.telegram.app import TelegramApp
from ia_suporte.integrations.telegram.sender import TelegramMessageSender
from ia_suporte.integrations.tiflux.simulator import TifluxWebhookSimulator
from ia_suporte.config import settings
from ia_suporte.messaging.registry import MessageSenderRegistry

def main():
    # endpoint inicial
    url = "/webhook/triage"
    base_url = "http://localhost:8000"

    # cria o registry de provedores de mensagens, nesse caso, apenas o Telegram
    message_senders = MessageSenderRegistry(
        factories={
            "telegram": lambda: TelegramMessageSender(
                token=settings.telegram_bot_token,
            ),
        },
    )

    # cria o simulador de webhook do Tiflux, que vai receber as mensagens do Telegram e enviar para o endpoint de triagem
    tiflux_simulator = TifluxWebhookSimulator(
        simulate_url=url,
        base_url=base_url,
        message_sender=message_senders.get(settings.message_sender_provider),
    )
    telegram_app = TelegramApp(token=settings.telegram_bot_token, handle_message=tiflux_simulator.post) 

    telegram_app.run_polling()

if __name__ == "__main__":
    main()