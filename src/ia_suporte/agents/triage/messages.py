import re
import unicodedata

from ia_suporte.templates.messages import MESSAGE_TEMPLATES, choose_random_message

from .schemas import SimpleMessageType

# nao gostei muito que esteja aqui, ver depois

_SIMPLE_MESSAGE_PATTERNS: tuple[
    tuple[SimpleMessageType, tuple[str, ...]]
] = (
    ("morning_greeting", ("bom dia",)),
    ("afternoon_greeting", ("boa tarde",)),
    ("evening_greeting", ("boa noite",)),
    ("well_being", ("tudo bem",)),
    ("hello", ("olá", "ola")),
)


def _normalize_message(message: str) -> str:
    normalized = unicodedata.normalize("NFKD", message)
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = re.sub(r"[!?.,;:]+", "", normalized)
    return " ".join(normalized.lower().split())


# rever e deixar em lugar mais acessivel, ver a do braitwaite
def detect_simple_message(message: str) -> SimpleMessageType | None:
    normalized = _normalize_message(message)
    for message_type, patterns in _SIMPLE_MESSAGE_PATTERNS:
        if normalized in patterns:
            return message_type
    return None


def choose_simple_message(
    message_type: SimpleMessageType,
    history: list[str],
) -> str:
    recent_responses = {
        entry.split(": ", maxsplit=1)[1]
        for entry in history
        if entry.startswith("triage_agent:") and ": " in entry
    }
    return choose_random_message(
        messages=MESSAGE_TEMPLATES,
        category=message_type,
        excluded=recent_responses,
    )
