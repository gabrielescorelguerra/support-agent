from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

from ia_suporte.agents.base import WebhookData
from ia_suporte.agents.triage.agent import TriageAgent
from ia_suporte.config import settings
from ia_suporte.llm.gemini import GeminiLLM


app = FastAPI()

gemini = GeminiLLM("gemini-3.1-flash-lite")

telegram_app = (
    Application.builder()
    .token(settings.telegram_bot_token)
    .updater(None)
    .build()
)


ROUTE_MESSAGES = {
    "FINANCEIRO": (
        "Seu atendimento foi direcionado para o setor financeiro."
    ),
    "SUPORTE": (
        "Seu atendimento foi direcionado para o suporte técnico."
    ),
    "COMERCIAL": (
        "Seu atendimento foi direcionado para o setor comercial."
    ),
    "NOTA_FISCAL": (
        "Seu atendimento foi direcionado para o setor de notas fiscais."
    ),
    "ATENDIMENTO_AVULSO": (
        "Seu atendimento foi direcionado para atendimento avulso."
    ),
    "MANUTENCAO_DE_EQUIPAMENTOS": (
        "Seu atendimento foi direcionado para manutenção de equipamentos."
    ),
    "ALTERACAO_DE_SISTEMA_E_ATUALIZACAO_CADASTRAL": (
        "Seu atendimento foi direcionado para alteração de sistema "
        "e atualização cadastral."
    ),
    "SUPRIMENTOS": (
        "Seu atendimento foi direcionado para suprimentos."
    ),
    "CONTRATOS": (
        "Seu atendimento foi direcionado para contratos."
    ),
    "SAC": (
        "Seu atendimento foi direcionado para o SAC."
    ),
    "MERCADO_LIVRE_E_RECLAME_AQUI": (
        "Seu atendimento foi direcionado para o setor responsável "
        "por Mercado Livre e Reclame Aqui."
    ),
    "CANCELAMENTO": (
        "Seu atendimento foi direcionado para cancelamento."
    ),
    "FILTRO": (
        "Seu atendimento será direcionado para um atendente."
    ),
    "TESTE_AGENTE": (
        "Teste de agente identificado."
    ),
}


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.message

    if message is None or message.text is None:
        return

    text = message.text.strip()

    # Reset
    if text.lower().startswith("reset"):
        context.user_data.clear()

        await message.reply_text(
            "O estado do bot foi reiniciado."
        )

        return

    state = context.user_data.get("state", "start")

    print(f"Received message from {message.from_user.first_name}: {text}, state: {state}")

    # Primeira interação
    if state == "start":
        await message.reply_text(
            "Olá! Eu sou o bot.\n\n"
            "Por favor, me diga como posso ajudá-lo."
        )

        context.user_data["state"] = "triage"

        return

    # Triagem
    if state == "triage":
        data = WebhookData(
            chat_id=message.chat_id,
            name=message.from_user.first_name,
            email="email@example.com",
            messages=[text],
        )

        agent = TriageAgent(
            llm=gemini,
            data=data,
        )

        response = agent.run()

        extra_params = response.contact_info.extra_params

        route = extra_params.get("route")
        confidence = extra_params.get("confidence")
        system = extra_params.get("system", "")
        product = extra_params.get("product", "")

        # Salva resultado completo da triagem
        context.user_data["triage"] = {
            "route": route,
            "confidence": confidence,
            "system": system,
            "product": product,
        }

        # Estado passa a ser a rota
        context.user_data["state"] = route

        # Mensagem retornada pelo agente
        await message.reply_text(response.response)

        # Mensagem boilerplate da rota
        route_message = ROUTE_MESSAGES.get(route)

        if route_message:
            await message.reply_text(route_message)

        return

    # Demais estados
    await message.reply_text(
        f"Estado atual: {state}"
    )


telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message,
    )
)


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()

    await telegram_app.bot.set_webhook(
        url=f"{settings.webhook_url}/telegram",
        secret_token=settings.telegram_webhook_secret,
    )


@app.on_event("shutdown")
async def shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()


@app.post("/telegram")
async def telegram_webhook(request: Request):
    update = Update.de_json(
        data=await request.json(),
        bot=telegram_app.bot,
    )

    await telegram_app.update_queue.put(update)

    return Response(status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok"}