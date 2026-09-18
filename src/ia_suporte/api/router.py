from fastapi import APIRouter
from ia_suporte.orchestration.webhook import process_webhook

from ia_suporte.schemas.output import TifluxResponse
from ia_suporte.schemas.tiflux import TifluxPayload

router = APIRouter()

@router.post("/webhook/triage", response_model=TifluxResponse)
async def triage(payload: TifluxPayload) -> TifluxResponse:
    return process_webhook(payload, department="triage")


@router.post("/webhook/support", response_model=TifluxResponse)
async def support(payload: TifluxPayload) -> TifluxResponse:
    return process_webhook(payload, department="support")
