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
    Application.builder().token(settings.telegram_bot_token).updater(None).build()
)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.message

    if message is None or message.text is None:
        return

    if message.text.startswith("reset"):
        context.user_data.clear()

        await message.reply_text("O estado do bot foi reiniciado.")

        return

    state = context.user_data.get("state", "start")

    if state == "start":
        await message.reply_text(
            "Olá, eu sou o bot! Por favor, me diga como posso ajudá-lo."
        )

        context.user_data["state"] = "triage"

        return

    if state == "triage":
        data = WebhookData(
            chat_id=message.chat_id,
            name=message.from_user.first_name,
            email="email@example.com",
            messages=[message.text],
        )

        agent = TriageAgent(
            llm=gemini,
            data=data,
        )

        response = agent.run()

        context.user_data["state"] = response.contact_info.extra_params["route"]
        state = context.user_data["state"]

        await message.reply_text(response.response)

    if state == "technical_support":
        await message.reply_text(
            "Você está no suporte técnico. "
            "Por favor, descreva o problema que você está enfrentando."
        )

    elif state == "commercial":
        await message.reply_text(
            "Você está no suporte comercial. "
            "Por favor, descreva sua dúvida sobre contratação, "
            "planos, preços, propostas ou vendas."
        )

    elif state == "financial":
        await message.reply_text(
            "Você está no suporte financeiro. "
            "Por favor, descreva sua dúvida sobre pagamentos, "
            "cobranças, boletos, faturas ou questões financeiras."
        )

    elif state == "other":
        await message.reply_text(
            "Você está no suporte geral. Por favor, descreva sua dúvida ou problema."
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
