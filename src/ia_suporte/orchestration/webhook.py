from functools import lru_cache
from ia_suporte.agents.support.agent import SupportAgent
from ia_suporte.agents.triage.agent import TriageAgent
from ia_suporte.llm.registry import LLMRegistry
from ia_suporte.persistence import ConversationStore

from ia_suporte.schemas.output import TifluxResponse
from ia_suporte.schemas.tiflux import TifluxPayload

# guarda o estado da conversa
# lru cache mantém o estado em cache para que não seja necessário buscar no banco de dados a cada requisição
@lru_cache
def get_store() -> ConversationStore:
    return ConversationStore()

# rever
@lru_cache
def get_llm_registry() -> LLMRegistry:
    return LLMRegistry()

# adiciona a mensagem do cliente ao histórico e cria o contexto
def _prepare_context(
    store: ConversationStore,
    payload: TifluxPayload,
    department: str,
):
    conversation = store.get_or_create_conversation(
        client_id=payload.client_id,
        conversation_id=payload.conversation_id,
    )
    conversation_id = conversation["conversation_id"]

    store.add_message(
        conversation_id=conversation_id,
        message_id=payload.message_id,
        author="CLIENT",
        text=payload.message,
        department=department.upper(),
    )

    return store.build_context(conversation)


# define o agente a ser usado com base no departamento
def _create_agent(context, department: str):
    llm_registry = get_llm_registry()

    if department == "triage":
        return TriageAgent(
            llm_registry=llm_registry,
            context=context,
        )

    return SupportAgent(
        llm_registry=llm_registry,
        context=context,
    )

# constroi a resposta a ser enviada de volta para o Tiflux
def _build_response(
    context,
    result,
) -> TifluxResponse:
    return TifluxResponse(
        conversation_id=context.conversation_id,
        client_id=context.client_id,
        response=result.response,
        department=result.department,
        metadata=result.metadata,
    )

# processa o webhook, cria o contexto, executa o agente e persiste o resultado
def process_webhook(payload: TifluxPayload, *, department: str) -> TifluxResponse:
    store = get_store()

    context = _prepare_context(
        store=store,
        payload=payload,
        department=department,
    )

    agent = _create_agent(
        context=context,
        department=department,
    )

    result = agent.run()
    store.persist_result(context, result)

    return _build_response(
        context=context,
        result=result,
    )
