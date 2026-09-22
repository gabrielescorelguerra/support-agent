import random
from collections.abc import Iterable, Mapping, Sequence

MessageCatalog = Mapping[str, Sequence[str]]

MESSAGE_TEMPLATES: dict[str, tuple[str, ...]] = {
    "initial_chat": (
        "Olá! Eu sou a Bia, assistente virtual da Tecnoponto. Como posso ajudar?",
        "Oi! Aqui é a Bia, da Tecnoponto. Me conte como posso ajudar você.",
        "Olá! Sou a Bia, assistente da Tecnoponto. O que você precisa resolver?",
        "Seja bem-vindo à Tecnoponto! Eu sou a Bia. Como posso ajudar?",
        "Olá! Eu sou a Bia e estou aqui pela Tecnoponto para ajudar. Em que posso ser útil?",
        "Oi! É um prazer falar com você. Sou a Bia, da Tecnoponto. Como posso ajudar?",
    ),
    "morning_greeting": (
        "Bom dia! Como posso ajudar?",
        "Bom dia, tudo bem? Como posso ajudar?",
        "Olá, bom dia! Como posso ajudar?",
        "Bom dia! Em que posso ajudar?",
        "Bom dia! O que você precisa?",
        "Bom dia! Pode me contar como posso ajudar?",
        "Olá! Bom dia! Estou à disposição.",
        "Um bom dia! Como posso ajudar?",
    ),
    "afternoon_greeting": (
        "Boa tarde! Como posso ajudar?",
        "Boa tarde, tudo bem? Como posso ajudar?",
        "Olá, boa tarde! Como posso ajudar?",
        "Boa tarde! Em que posso ajudar?",
        "Boa tarde! O que você precisa?",
        "Boa tarde! Pode me contar como posso ajudar?",
        "Olá! Boa tarde! Estou à disposição.",
        "Uma boa tarde! Como posso ajudar?",
    ),
    "evening_greeting": (
        "Boa noite! Como posso ajudar?",
        "Boa noite, tudo bem? Como posso ajudar?",
        "Olá, boa noite! Como posso ajudar?",
        "Boa noite! Em que posso ajudar?",
        "Boa noite! O que você precisa?",
        "Boa noite! Pode me contar como posso ajudar?",
        "Olá! Boa noite! Estou à disposição.",
        "Uma boa noite! Como posso ajudar?",
    ),
    "well_being": (
        "Tudo bem! Como posso ajudar?",
        "Tudo bem por aqui! E com você?",
        "Olá! Tudo bem? Como posso ajudar?",
        "Tudo certo! Em que posso ajudar?",
        "Tudo bem! O que você precisa?",
        "Tudo bem, sim. Como posso ajudar?",
        "Por aqui, tudo bem! Estou à disposição.",
        "Tudo bem? Pode me contar como posso ajudar.",
    ),
    "hello": (
        "Olá! Como posso ajudar?",
        "Olá, tudo bem? Como posso ajudar?",
        "Oi! Como posso ajudar?",
        "Olá! Em que posso ajudar?",
        "Olá! O que você precisa?",
        "Olá! Pode me contar como posso ajudar?",
        "Oi, tudo bem? Estou à disposição.",
        "Olá! Estou à disposição para ajudar.",
    ),
}


def choose_random_message(
    messages: MessageCatalog,
    category: str,
    excluded: Iterable[str] = (),
) -> str:
    try:
        options = tuple(messages[category])
    except KeyError as error:
        raise ValueError(
            f"Message category '{category}' is not configured"
        ) from error

    if not options:
        raise ValueError(f"Message category '{category}' has no options")

    excluded_set = set(excluded)
    available_options = tuple(
        option for option in options if option not in excluded_set
    )
    return random.SystemRandom().choice(available_options or options)
