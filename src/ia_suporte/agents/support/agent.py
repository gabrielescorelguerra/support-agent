import json

from ia_suporte.agents.base import AgentResponse, ContactInfo, WebhookData
from ia_suporte.llm.base import LLM

from .prompt import build_analysis_prompt, build_response_prompt
from .schemas import SupportAnalysis


class SupportAgent:
    def __init__(self, llm: LLM, data: WebhookData):
        self.llm = llm
        self.history = data.messages
        self.data = data

    def run(self) -> AgentResponse:
        analysis = self._analyze()
        response = self._build_response(analysis)

        return self._build_agent_response(
            analysis=analysis,
            response=response,
        )

    def _analyze(self) -> SupportAnalysis:
        prompt = build_analysis_prompt(
            history=self.history,
        )

        response = self.llm.generate(prompt=prompt)
        data = json.loads(response)

        return SupportAnalysis.model_validate(data)

    def _build_response(
        self,
        analysis: SupportAnalysis,
    ) -> str:
        prompt = build_response_prompt(
            history=self.history,
            analysis=analysis,
        )

        return self.llm.generate(prompt=prompt)

    def _build_agent_response(
        self,
        analysis: SupportAnalysis,
        response: str,
    ) -> AgentResponse:

        extra_params = {
            "route": analysis.route,
            "confidence": analysis.confidence,
            "system": analysis.system,
            "product": analysis.product,
            "situation": analysis.situation,
            "next_action": analysis.next_action,
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