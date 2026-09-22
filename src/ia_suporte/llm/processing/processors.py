import re


class NormalizeWhitespace:
    def process(self, text: str) -> str:
        """Normaliza os espaços em branco."""
        lines = (" ".join(line.split()) for line in text.splitlines())
        return "\n".join(line for line in lines if line)


class RedactSensitiveData:
    _EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )
    _PHONE_PATTERN = re.compile(
        r"(?<!\d)(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?"
        r"(?:9?\d{4}[-\s]?\d{4})(?!\d)"
    )
    _CPF_PATTERN = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")

    def process(self, text: str) -> str:
        """Redige informações sensíveis, como e-mails, números de telefone e CPFs, por meio de expressões regulares."""
        text = self._EMAIL_PATTERN.sub("[EMAIL_CENSURADO]", text)
        text = self._CPF_PATTERN.sub("[CPF_CENSURADO]", text)
        return self._PHONE_PATTERN.sub("[TELEFONE_CENSURADO]", text)


def format_history(history: list[str]) -> str:
    """Formata o histórico de mensagens para exibição."""
    return "\n".join(history) or "(sem histórico)"


# _SMALL_TALK_PATTERNS = (
#     re.compile(
#         r"^(oi|olá|ola|bom dia|boa tarde|boa noite)[!. ]*$",
#         re.IGNORECASE,
#     ),
#     re.compile(
#         r"^(tudo bem|como vai|obrigado|obrigada)[!. ?]*$",
#         re.IGNORECASE,
#     ),
# )

# def is_small_talk(text: str) -> bool:
#     normalized = " ".join(text.split()).strip()
#     return any(pattern.fullmatch(normalized) for pattern in _SMALL_TALK_PATTERNS)