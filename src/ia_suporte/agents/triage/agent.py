import json

from ia_suporte.agents.base import AgentContext, AgentResult
from ia_suporte.llm.registry import LLMRegistry

from .prompt import build_analysis_prompt, build_review_prompt
from .schemas import TriageAnalysis


class TriageAgent:
    def __init__(self, llm_registry: LLMRegistry, context: AgentContext):
        self.llm_registry = llm_registry
        self.context = context
        self.history = context.history

    def run(self) -> AgentResult:
        analysis = self._analyze()

        print("Agente de triagem...")

        if self._is_confident(analysis):
            response = self._build_confident_response(analysis)
        else:
            response = self._build_review_response()

        return self._build_agent_result(
            analysis=analysis,
            response=response,
        )


    def _analyze(self) -> TriageAnalysis:
        print("Analisando a conversa para determinar o departamento e a rota...")

        prompt = build_analysis_prompt(
            history=self.history,
        )

        response = self.llm_registry.get("triage_analysis").generate(prompt=prompt)
        data = json.loads(response)

        return TriageAnalysis.model_validate(data)

    def _is_confident(self, analysis: TriageAnalysis) -> bool:
        return analysis.confidence == 1

    def _build_confident_response(
        self,
        analysis: TriageAnalysis,
    ) -> str:
        print("Tenho certeza sobre o departamento e a rota, então vou transferir o atendimento...")
        
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
        print("Não tenho certeza sobre o departamento e a rota, então vou pedir uma revisão...")
        prompt = build_review_prompt(
            history=self.history,
        )

        return self.llm_registry.get("triage_review").generate(prompt=prompt)


    def _build_agent_result(
        self,
        analysis: TriageAnalysis,
        response: str,
    ) -> AgentResult:
        extra_params = {
            "route": analysis.route,
            "confidence": analysis.confidence,
            "system": analysis.system,
            "product": analysis.product,
        }

        return AgentResult(
            response=response,
            department=analysis.route or self.context.department or "triage",
            metadata=extra_params,
        )