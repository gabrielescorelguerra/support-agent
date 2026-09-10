from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

from ia_suporte.agents.base import WebhookData
from ia_suporte.agents.support.agent import SupportAgent
from ia_suporte.agents.triage.agent import TriageAgent
from ia_suporte.config import settings
from ia_suporte.llm.gemini import GeminiLLM


gemini = GeminiLLM("gemini-3.1-flash-lite")


ROUTE_MESSAGES = {
    "FINANCEIRO": "Seu atendimento foi direcionado para o setor financeiro.",
    "SUPORTE": "Olá sou o agente de suporte técnico. Em que posso ajudá-lo?",
    "COMERCIAL": "Seu atendimento foi direcionado para o setor comercial.",
    "NOTA_FISCAL": "Seu atendimento foi direcionado para o setor de notas fiscais.",
    "ATENDIMENTO_AVULSO": "Seu atendimento foi direcionado para atendimento avulso.",
    "MANUTENCAO_DE_EQUIPAMENTOS":
        "Seu atendimento foi direcionado para manutenção de equipamentos.",
    "ALTERACAO_DE_SISTEMA_E_ATUALIZACAO_CADASTRAL":
        "Seu atendimento foi direcionado para alteração de sistema e atualização cadastral.",
    "SUPRIMENTOS": "Seu atendimento foi direcionado para suprimentos.",
    "CONTRATOS": "Seu atendimento foi direcionado para contratos.",
    "SAC": "Seu atendimento foi direcionado para o SAC.",
    "MERCADO_LIVRE_E_RECLAME_AQUI":
        "Seu atendimento foi direcionado para o setor responsável por Mercado Livre e Reclame Aqui.",
    "CANCELAMENTO": "Seu atendimento foi direcionado para cancelamento.",
    "FILTRO": "Seu atendimento será direcionado para um atendente.",
    "TESTE_AGENTE": "Teste de agente identificado.",
}

MAX_HISTORY_LENGTH = 8


def update_history(context, history: list[str]) -> list[str]:
    trimmed_history = history[-MAX_HISTORY_LENGTH:]
    context.user_data["messages"] = trimmed_history
    return trimmed_history


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.message

    if message is None or message.text is None:
        return

    text = message.text.strip()

    if text.lower().startswith("reset"):
        context.user_data.clear()
        await message.reply_text("O estado do bot foi reiniciado.")
        return

    state = context.user_data.get("state", "start")

    print(
        f"Received message from "
        f"{message.from_user.first_name}: {text}, state: {state}"
    )

    if state == "start":
        await message.reply_text(
            "Olá! Eu sou o bot.\n\n"
            "Por favor, me diga como posso ajudá-lo."
        )

        context.user_data["state"] = "triage"
        context.user_data["messages"] = []
        return

    history = list(context.user_data.get("messages", []))
    data = WebhookData(
        chat_id=message.chat_id,
        name=message.from_user.first_name,
        email="email@example.com",
        messages=history + ["USER: " + text],
    )
    context.user_data["messages"] = data.messages

    if state == "SUPORTE":
        agent = SupportAgent(
            llm=gemini,
            data=data
        )

        response = agent.run()
        context.user_data["messages"] = update_history(
            context,
            data.messages,
        )

        await message.reply_text(response.response)

        return

    if state == "triage":

        agent = TriageAgent(
            llm=gemini,
            data=data,
        )

        response = agent.run()
        context.user_data["messages"] = update_history(
            context,
            data.messages + [f"BOT: {response.response}"],
        )

        extra_params = response.contact_info.extra_params

        route = extra_params.get("route")
        confidence = extra_params.get("confidence")
        system = extra_params.get("system", "")
        product = extra_params.get("product", "")

        context.user_data["extra_params"] = {
            "route": route,
            "confidence": confidence,
            "system": system,
            "product": product,
        }

        print(
            f"Extra Params: "
            f"route={route}, "
            f"confidence={confidence}, "
            f"system={system}, "
            f"product={product}"
        )

        if confidence == 1:
            context.user_data["state"] = route

        await message.reply_text(response.response)

        if confidence == 1:
            route_message = ROUTE_MESSAGES.get(route)

            if route_message:
                await message.reply_text(route_message)

        return

    await message.reply_text(
        f"Estado atual: {state}"
    )


def main():
    telegram_app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("Bot iniciado em polling...")

    telegram_app.run_polling()


if __name__ == "__main__":
    main()