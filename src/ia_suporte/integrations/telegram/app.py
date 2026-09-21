from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

# classe responsavel pelo inicio e funcionamento do bot
class TelegramApp:
    def __init__(self, token: str, handle_message):
        self.token = token
        self.app = Application.builder().token(self.token).build()

        # adiciona o handler para lidar com mensagens de texto recebidas
        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_message,
            )
        )

    def run_polling(self):
        print("Bot iniciado em polling...")
        self.app.run_polling()

    async def send_message(self, chat_id: int, text: str):
        """Envia uma mensagem para o chat especificado."""
        await self.app.bot.send_message(chat_id=chat_id, text=text)
    
