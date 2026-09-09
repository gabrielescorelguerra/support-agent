import json

from ia_suporte.agents.base import AgentResponse, ContactInfo, WebhookData
from ia_suporte.llm.base import LLM

from .prompt import *
from .schemas import TriageAnalysis


class TriageAgent:
    def __init__(self, llm: LLM, data: WebhookData):
        self.llm = llm
        self.history = data.messages
        self.data = data

    # ponto de entrada para executar a triagem
    def run(self) -> AgentResponse:
        analysis = self._analyze()

        if self._is_confident(analysis):
            response = self._build_confident_response(analysis=analysis)
        else:
            response = self._build_review_response(analysis=analysis)
            analysis.route = "triage"

        return self._build_agent_response(analysis=analysis, response=response)

    # análise da conversa e geracao de resposta de analise
    def _analyze(self) -> TriageAnalysis:
        # depois ver structured output
        prompt = build_analysis_prompt(history=self.history)
        response = self.llm.generate(prompt=prompt)
        data = json.loads(response)

        return TriageAnalysis.model_validate(data)

    # verifica se a analise e confiante (confianca == 1)
    def _is_confident(self, analysis: TriageAnalysis):
        return analysis.confidence == 1

    # constroi a resposta para analise confiante (confianca == 1)
    def _build_confident_response(self, analysis: TriageAnalysis) -> str:
        route_names = {
            "technical_support": "suporte técnico",
            "commercial": "suporte comercial",
            "financial": "suporte financeiro",
            "other": "suporte geral",
        }
        route = analysis.route
        return f"Sua conversa está sendo transferida para o setor de {route_names.get(route, 'suporte geral')}."

    # constroi a resposta para analise nao confiante (confianca == 0)
    def _build_review_response(self, analysis: TriageAnalysis) -> str:
        prompt = build_review_prompt(history=self.history)

        return self.llm.generate(prompt=prompt)

    # constroi a resposta do agente com base na analise e na resposta gerada
    def _build_agent_response(
        self, analysis: TriageAnalysis, response: str
    ) -> AgentResponse:
        extra_params = {
            "system": analysis.system,
            "confidence": analysis.confidence,
            "product": analysis.product,
            "route": analysis.route,
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
