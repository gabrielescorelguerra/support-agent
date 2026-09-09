import json

from ia_suporte.agents.base import AgentResponse, ContactInfo, WebhookData
from ia_suporte.llm.base import LLM

from .prompt import build_analysis_prompt, build_review_prompt
from .schemas import TriageAnalysis


class TriageAgent:
    def __init__(self, llm: LLM, data: WebhookData):
        self.llm = llm
        self.history = data.messages
        self.data = data

    def run(self) -> AgentResponse:
        analysis = self._analyze()

        if self._is_confident(analysis):
            response = self._build_confident_response(analysis)
        else:
            response = self._build_review_response()

        return self._build_agent_response(
            analysis=analysis,
            response=response,
        )

    def _analyze(self) -> TriageAnalysis:
        prompt = build_analysis_prompt(
            history=self.history,
        )

        response = self.llm.generate(prompt=prompt)
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
            f"Sua conversa está sendo transferida "
            f"para o setor de {route_name}."
        )

    def _build_review_response(self) -> str:
        prompt = build_review_prompt(
            history=self.history,
        )

        return self.llm.generate(prompt=prompt)

    def _build_agent_response(
        self,
        analysis: TriageAnalysis,
        response: str,
    ) -> AgentResponse:
        extra_params = {
            "route": analysis.route,
            "confidence": analysis.confidence,
            "system": analysis.system,
            "product": analysis.product,
        }

        contact_info = ContactInfo(
            name=self.data.name,
            email=self.data.email,
            extra_params=extra_params,
        )

        return AgentResponse(
            action="send_message",
            chat_id=self.data.chat_id,
            response=response,
            contact_info=contact_info,
        )