from telegram import Bot

from ia_suporte.messaging.base import MessageSender


# classe concreta para envio de mensagens via Telegram, implementando a interface MessageSender
class TelegramMessageSender(MessageSender):
    def __init__(self, token: str) -> None:
        self.bot = Bot(token=token)

    async def send_message(self, recipient_id: str, text: str) -> None:
        await self.bot.send_message(chat_id=int(recipient_id), text=text)
