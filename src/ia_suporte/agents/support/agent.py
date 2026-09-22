import json
import logging

from ia_suporte.agents.base import AgentContext, AgentResult
from ia_suporte.llm.registry import LLMRegistry

from .prompt import build_classify_prompt, build_knowledge_base_prompt
from .schemas import SupportClassification

logger = logging.getLogger(__name__)


class SupportAgent:
    def __init__(self, llm_registry: LLMRegistry, context: AgentContext):
        self.llm_registry = llm_registry
        self.context = context
        self.history = context.history

    def run(self) -> AgentResult:
        logger.info(
            "Starting support agent",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "department": self.context.department or "support",
                "history_size": len(self.history),
            },
        )
        classification: SupportClassification = self._classify()

        if classification.classification == "KNOWLEDGE_BASE":
            logger.info(
                "Support classification requires knowledge base",
                extra={
                    "conversation_id": str(self.context.conversation_id),
                    "route": classification.route,
                },
            )
            message = self._query_knowledge_base()
        else:
            logger.info(
                "Support classification uses direct response",
                extra={
                    "conversation_id": str(self.context.conversation_id),
                    "classification": classification.classification,
                    "route": classification.route,
                },
            )
            message = classification.message

        result = self._build_agent_result(
            response=message,
            classification=classification
        )
        logger.info(
            "Finished support agent",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "classification": classification.classification,
                "route": result.department,
                "status": result.status,
            },
        )
        return result


    def _classify(self) -> SupportClassification:
        logger.info(
            "Starting support classification",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "history_size": len(self.history),
            },
        )
        prompt = build_classify_prompt(
            history=self.history,
        )

        message = self.llm_registry.get(
            "support_classification"
        ).generate(prompt=prompt)
        classification = SupportClassification.model_validate(json.loads(message))
        logger.info(
            "Support classification completed",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "classification": classification.classification,
                "route": classification.route,
            },
        )
        return classification

    def _query_knowledge_base(self) -> str:
        logger.info(
            "Starting knowledge base response",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "history_size": len(self.history),
            },
        )
        prompt = build_knowledge_base_prompt(history=self.history)
        response = self.llm_registry.get("support_knowledge_base").generate(
            prompt=prompt
        )
        logger.info(
            "Knowledge base response completed",
            extra={"conversation_id": str(self.context.conversation_id)},
        )
        return response


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