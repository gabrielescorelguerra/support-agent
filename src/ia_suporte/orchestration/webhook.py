import logging
from functools import lru_cache
from ia_suporte.agents.support.agent import SupportAgent
from ia_suporte.agents.triage.agent import TriageAgent
from ia_suporte.llm.processing.pipeline import get_text_processing_pipeline
from ia_suporte.llm.registry import LLMRegistry
from ia_suporte.templates.messages import MESSAGE_TEMPLATES, choose_random_message
from ia_suporte.persistence import ConversationStore

from ia_suporte.schemas.output import TifluxResponse
from ia_suporte.schemas.tiflux import TifluxPayload

logger = logging.getLogger(__name__)

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
    processed_message: str,
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
        original_text=payload.message,
        processed_text=processed_message,
        department=department,
    )

    context = store.build_context(conversation)
    context.original_message = payload.message
    context.processed_message = processed_message
    return context


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


def _run_agent(context, department: str):
    return _create_agent(context=context, department=department).run()

# constroi a resposta a ser enviada de volta para o Tiflux
def _build_response(
    payload: TifluxPayload,
    result,
) -> TifluxResponse:
    route = str(result.metadata.get("route") or result.department)

    return TifluxResponse(
        chat_id=int(payload.client_id),
        contact_info={
            "name": payload.client_name,
            "email": payload.client_email or None,
            "extra_params": {
                "message": result.response,
                "route": route,
            },
        },
    )

# processa o webhook, cria o contexto, executa o agente e persiste o resultado
def process_webhook(payload: TifluxPayload, *, department: str) -> TifluxResponse:
    store = get_store()
    processed_message = get_text_processing_pipeline(department).process(
        payload.message
    )
    logger.info(
        "Processing webhook",
        extra={
            "conversation_id": str(payload.conversation_id),
            "department": department,
            "message_length": len(payload.message),
            "processed_message_length": len(processed_message),
        },
    )

    context = _prepare_context(
        store=store,
        payload=payload,
        department=department,
        processed_message=processed_message,
    )
    result = _run_agent(context=context, department=department)
    store.persist_result(context, result)

    logger.info(
        "Webhook processed",
        extra={
            "conversation_id": str(payload.conversation_id),
            "input_department": department,
            "output_department": result.department,
            "history_size": len(context.history),
        },
    )

    return _build_response(payload=payload, result=result)


def build_start_response(payload: TifluxPayload) -> TifluxResponse:
    return TifluxResponse(
        chat_id=int(payload.client_id),
        contact_info={
            "name": payload.client_name,
            "email": payload.client_email or None,
            "extra_params": {
                "message": (
                    choose_random_message(
                        messages=MESSAGE_TEMPLATES,
                        category="initial_chat",
                    )
                ),
                "route": "triage",
            },
        },
    )
