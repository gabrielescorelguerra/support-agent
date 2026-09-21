from __future__ import annotations

from collections.abc import Callable

from ia_suporte.messaging.base import MessageSender

# uma factory é uma função que cria um objeto, nesse caso, um MessageSender. A ideia é que cada provedor de mensagens (como Telegram, WhatsApp, etc.) tenha sua própria factory que sabe como criar o MessageSender correspondente.
# nesse caso, a factory é uma função que não recebe argumentos e retorna um MessageSender.
MessageSenderFactory = Callable[[], MessageSender]

# ele não precisa saber qual o provedor de mensagens, ele só precisa saber qual o provedor de mensagens que ele quer usar
# e procura na classe dele a funcao de envio de mensagens (send_message)


# Registry for managing different message sender implementations.
class MessageSenderRegistry:
    """Resolves a message sender while keeping providers replaceable."""

    def __init__(
        self,
        factories: dict[str, MessageSenderFactory] | None = None,
    ) -> None:
        self._factories = factories or {}

    def register(self, provider: str, factory: MessageSenderFactory) -> None:
        # guarda o factory como um dicionario, onde a chave eh o nome e o valor eh a funcao que cria o objeto
        self._factories[provider] = factory

    # procura o factory do provedor de mensagens e chama ele para criar o objeto MessageSender
    def get(self, provider: str) -> MessageSender:
        try:
            factory = self._factories[provider]
        except KeyError as error:
            available = ", ".join(sorted(self._factories))
            raise ValueError(
                f"Unsupported message sender '{provider}'. "
                f"Available providers: {available}"
            ) from error
        return factory()
