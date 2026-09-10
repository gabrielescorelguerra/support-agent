import json

from ia_suporte.agents.base import AgentResponse, ContactInfo, WebhookData
from ia_suporte.llm.base import LLM

from .prompt import build_classify_prompt
from .schemas import SupportClassification


class SupportAgent:
    def __init__(self, llm: LLM, data: WebhookData):
        self.llm = llm
        self.history = data.messages
        self.data = data

    def run(self) -> AgentResponse:
        classification: SupportClassification = self._classify()
        print(f"Classificação: {classification.classification}, Rota: {classification.route}")

        if classification.classification == "KNOWLEDGE_BASE":
            print("Consulta a base de conhecimento")
            message = "Consultando a base, o historico da conversa é: " + " | ".join(self.history)
        else:
            message = classification.message

        self.data.messages.append("BOT: " + message)

        return self._build_agent_response(
            response=message,
            classification=classification
        )


    def _classify(self) -> SupportClassification:
        prompt = build_classify_prompt(
            history=self.history,
        )

        message = self.llm.generate(prompt=prompt)
        return SupportClassification.model_validate(json.loads(message))


    def _build_agent_response(
        self,
        response: str,
        classification: SupportClassification
    ) -> AgentResponse:

        extra_params = {
            "classification": classification.classification,
            "route": classification.route,
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