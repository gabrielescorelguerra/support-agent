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

        if self._is_confident(analysis):
            response = self._build_confident_response(analysis)
        else:
            response = self._build_review_response()

        return self._build_agent_result(
            analysis=analysis,
            response=response,
        )

    def _analyze(self) -> TriageAnalysis:
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
        route_names = {
            "FINANCEIRO": "financeiro",
            "SUPORTE": "suporte técnico",
            "COMERCIAL": "comercial",
            "NOTA_FISCAL": "notas fiscais",
            "ATENDIMENTO_AVULSO": "atendimento avulso",
            "MANUTENCAO_DE_EQUIPAMENTOS": "manutenção de equipamentos",
            "ALTERACAO_DE_SISTEMA_E_ATUALIZACAO_CADASTRAL":
                "alteração de sistema e atualização cadastral",
            "SUPRIMENTOS": "suprimentos",
            "CONTRATOS": "contratos",
            "SAC": "SAC",
            "MERCADO_LIVRE_E_RECLAME_AQUI":
                "Mercado Livre e Reclame Aqui",
            "CANCELAMENTO": "cancelamento",
            "FILTRO": "atendimento",
            "TESTE_AGENTE": "teste do agente",
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
            department=analysis.route or self.context.department or "TRIAGE",
            metadata=extra_params,
        )