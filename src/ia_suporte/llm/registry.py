from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ia_suporte.config import Settings, settings
from ia_suporte.llm.base import LLM
from ia_suporte.llm.gemini import GeminiLLM

LLMFactory = Callable[[str], LLM]

# depois dar uma olhada

@dataclass(frozen=True)
class LLMSelection:
    provider: str
    model: str


class LLMRegistry:
    """Resolves an LLM by use case while keeping providers replaceable."""

    def __init__(
        self,
        config: Settings = settings,
        factories: dict[str, LLMFactory] | None = None,
    ) -> None:
        self.config = config
        self._factories: dict[str, LLMFactory] = factories or {
            "gemini": lambda model: GeminiLLM(
                model=model,
                api_key=config.gemini_api_key,
            ),
        }

    def register(self, provider: str, factory: LLMFactory) -> None:
        self._factories[provider] = factory

    def selection_for(self, use_case: str) -> LLMSelection:
        provider = getattr(self.config, f"{use_case}_llm_provider")
        model = getattr(self.config, f"{use_case}_llm_model")
        return LLMSelection(provider=provider, model=model)

    def get(self, use_case: str) -> LLM:
        selection = self.selection_for(use_case)
        try:
            factory = self._factories[selection.provider]
        except KeyError as error:
            available = ", ".join(sorted(self._factories))
            raise ValueError(
                f"Unsupported LLM provider '{selection.provider}' for "
                f"use case '{use_case}'. Available providers: {available}"
            ) from error
        return factory(selection.model)
