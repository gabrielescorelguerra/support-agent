import json

from ia_suporte.agents.base import AgentContext, AgentResult
from ia_suporte.llm.registry import LLMRegistry

from .prompt import build_classify_prompt, build_knowledge_base_prompt
from .schemas import SupportClassification


class SupportAgent:
    def __init__(self, llm_registry: LLMRegistry, context: AgentContext):
        self.llm_registry = llm_registry
        self.context = context
        self.history = context.history

    def run(self) -> AgentResult:
        classification: SupportClassification = self._classify()

        print("Agente de suporte...")

        if classification.classification == "KNOWLEDGE_BASE":
            print("Consulta a base de conhecimento")
            message = self._query_knowledge_base()
        else:
            message = classification.message

        return self._build_agent_result(
            response=message,
            classification=classification
        )


    def _classify(self) -> SupportClassification:
        prompt = build_classify_prompt(
            history=self.history,
        )

        message = self.llm_registry.get(
            "support_classification"
        ).generate(prompt=prompt)
        return SupportClassification.model_validate(json.loads(message))

    def _query_knowledge_base(self) -> str:
        prompt = build_knowledge_base_prompt(history=self.history)
        return self.llm_registry.get("support_knowledge_base").generate(
            prompt=prompt
        )


    def _build_agent_result(
        self,
        response: str,
        classification: SupportClassification
    ) -> AgentResult:

        extra_params = {
            "classification": classification.classification,
            "route": classification.route,
        }

        return AgentResult(
            response=response,
            department=classification.route,
            status="CLOSED" if classification.classification == "END" else "IN_PROGRESS",
            metadata=extra_params,
        )