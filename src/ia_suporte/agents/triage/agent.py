import json
import logging

from ia_suporte.agents.base import AgentContext, AgentResult
from ia_suporte.llm.registry import LLMRegistry

from .messages import choose_simple_message, detect_simple_message
from .prompt import build_analysis_prompt, build_review_prompt
from .schemas import SimpleMessageType, TriageAnalysis

logger = logging.getLogger(__name__)


class TriageAgent:
    def __init__(self, llm_registry: LLMRegistry, context: AgentContext):
        self.llm_registry = llm_registry
        self.context = context
        self.history = context.history

    def run(self) -> AgentResult:
        logger.info(
            "Starting triage agent",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "department": self.context.department or "triage",
                "history_size": len(self.history),
            },
        )
        # se a mensagem for simples, como um cumprimento, responde de forma determinística
        simple_message_type = detect_simple_message(
            self.context.processed_message
        )
        if simple_message_type is not None:
            response = choose_simple_message(
                message_type=simple_message_type,
                history=self.history,
            )
            result = self._build_agent_result(
                analysis=None,
                response=response,
                simple_message_type=simple_message_type,
            )
            logger.info(
                "Built deterministic simple-message response",
                extra={
                    "conversation_id": str(self.context.conversation_id),
                    "simple_message_type": simple_message_type,
                },
            )
            return result

        # se nao for simples, faz analise com LLM
        analysis = self._analyze()

        if self._is_confident(analysis):
            response = self._build_confident_response(analysis)
        else:
            response = self._build_review_response()

        result = self._build_agent_result(
            analysis=analysis,
            response=response,
        )
        logger.info(
            "Finished triage agent",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "route": result.metadata.get("route"),
                "confidence": result.metadata.get("confidence"),
                "response_mode": (
                    "transfer" if analysis.confidence == 1 else "clarification"
                ),
            },
        )
        return result


    def _analyze(self) -> TriageAnalysis:
        logger.info(
            "Starting triage classification",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "history_size": len(self.history),
            },
        )

        prompt = build_analysis_prompt(
            history=self.history,
        )

        response = self.llm_registry.get("triage_analysis").generate(prompt=prompt)
        data = json.loads(response)
        analysis = TriageAnalysis.model_validate(data)
        logger.info(
            "Triage classification completed",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "route": analysis.route,
                "confidence": analysis.confidence,
                "sentiment": analysis.sentiment,
                "has_system": bool(analysis.system),
                "has_product": bool(analysis.product),
            },
        )
        return analysis

    def _is_confident(self, analysis: TriageAnalysis) -> bool:
        return analysis.confidence == 1

    def _build_confident_response(
        self,
        analysis: TriageAnalysis,
    ) -> str:
        """Constrói uma resposta de transferência para o departamento apropriado, com base na análise do LLM."""
        logger.info(
            "Building triage transfer response",
            extra={
                "conversation_id": str(self.context.conversation_id),
                "route": analysis.route,
            },
        )
        
        route_names = {
            "finance": "financeiro",
            "support": "suporte técnico",
            "commercial": "comercial",
            "invoice": "notas fiscais",
            "ad_hoc_support": "atendimento avulso",
            "equipment_maintenance": "manutenção de equipamentos",
            "system_and_customer_data_update":
                "alteração de sistema e atualização cadastral",
            "supplies": "suprimentos",
            "contracts": "contratos",
            "customer_service": "SAC",
            "marketplace_and_complaints":
                "Mercado Livre e Reclame Aqui",
            "cancellation": "cancelamento",
            "human_support": "atendimento",
            "agent_test": "teste do agente",
        }

        route_name = route_names.get(
            analysis.route,
            "atendimento",
        )

        return (
            f"Certo, vou transferir o seu atendimento "
            f"para o setor de {route_name}!"
        )


    def _build_review_response(self) -> str:
        logger.info(
            "Building triage clarification response",
            extra={
                "conversation_id": str(self.context.conversation_id),
            },
        )
        prompt = build_review_prompt(
            history=self.history,
        )

        return self.llm_registry.get("triage_review").generate(prompt=prompt)


    def _build_agent_result(
        self,
        analysis: TriageAnalysis | None,
        response: str,
        simple_message_type: SimpleMessageType | None = None,
    ) -> AgentResult:
        extra_params = {
            "route": analysis.route if analysis else None,
            "confidence": analysis.confidence if analysis else 1,
            "system": analysis.system if analysis else "",
            "product": analysis.product if analysis else "",
        }
        if simple_message_type is not None:
            extra_params["simple_message_type"] = simple_message_type

        return AgentResult(
            response=response,
            department=(
                analysis.route
                if analysis and analysis.route
                else self.context.department or "triage"
            ),
            metadata=extra_params,
        )