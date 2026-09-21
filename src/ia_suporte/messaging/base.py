from abc import ABC, abstractmethod


# classe abstrata para envio de mensagens, que pode ser implementada por diferentes provedores
class MessageSender(ABC):
    @abstractmethod
    async def send_message(self, recipient_id: str, text: str) -> None:
        """Send text to a recipient identified by the provider."""
        raise NotImplementedError
