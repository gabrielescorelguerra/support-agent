## Fluxo da aplicação

```text
Telegram
   -> TelegramApp
   -> TifluxWebhookSimulator
   -> FastAPI /webhook/triage
   -> agente de IA
   -> resposta do webhook
   -> MessageSender
   -> Telegram
```

O `TifluxWebhookSimulator` usa a abstração `MessageSender` para enviar a
resposta ao usuário. A implementação atual é `TelegramMessageSender`, mas
outros provedores podem ser adicionados sem alterar o simulador.

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua-chave
TELEGRAM_BOT_TOKEN=seu-token
TELEGRAM_WEBHOOK_SECRET=seu-segredo
WEBHOOK_URL=http://localhost:8000/telegram_webhook
MESSAGE_SENDER_PROVIDER=telegram
```

`MESSAGE_SENDER_PROVIDER` define o provedor usado para responder ao usuário.
Atualmente, o provedor implementado é `telegram`.

## LLM selection

LLMs are selected by stage through `LLMRegistry`. Each stage can use a
different provider and model:

```env
triage_analysis_llm_provider=gemini
triage_analysis_llm_model=gemini-3.1-flash-lite
triage_review_llm_provider=gemini
triage_review_llm_model=gemini-3.1-flash
support_classification_llm_provider=gemini
support_classification_llm_model=gemini-3.1-flash-lite
support_knowledge_base_llm_provider=gemini
support_knowledge_base_llm_model=gemini-3.1-pro
```

The configured stages are:

- `triage_analysis`: classifies the conversation and extracts system/product.
- `triage_review`: asks for missing information when classification is uncertain.
- `support_classification`: identifies the support action and route.
- `support_knowledge_base`: generates the technical answer.

New providers can be added without changing agents:

```python
registry.register("provider_name", factory)
```

## MessageSender

O registro de remetentes segue o mesmo padrão do `LLMRegistry`:

```python
message_senders.register("provider_name", factory)
sender = message_senders.get("provider_name")
await sender.send_message(recipient_id="123", text="Olá")
```

## Execução local

Inicie o FastAPI:

```powershell
uv run uvicorn ia_suporte.api.app:app --host 127.0.0.1 --port 8000
```

Em outro terminal, inicie o bot:

```powershell
uv run ia-suporte
```

O FastAPI precisa estar em execução antes do envio de mensagens pelo Telegram,
pois o simulador chama `http://localhost:8000/webhook/triage`.

Também é possível executar diretamente pelo ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m uvicorn ia_suporte.api.app:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m ia_suporte.main
```

---

# Melhorias

departamento ta errado, ta indo o do futuro, nao o que
pegar o do futuro pelo campo personalizado e mudar url de post
Simula webhook usando polling

Quando há mensagens enviadas, chama router, enviando uma simulação do payload do TiFlux

Da para transformar mensagens grandes em streams - gabriel routes_secullumia.py

### Melhorias no historico

No seu projeto, o histórico é construído pelo  ConversationStore  e passado aos agentes. Um processador pode operar sobre o prompt completo, mas isso dificulta distinguir:

• instruções do sistema;
• histórico;
• mensagem atual;
• formato de saída.

Uma alternativa mais robusta seria criar um objeto estruturado antes da montagem:

class PromptContext(BaseModel):
    system_instructions: str
    history: list[str]
    current_message: str
    output_format: str

o pipeline de limpeza pode ser chamado dentro de cada agente e definido dentro de suas pastas -> bom colocar em build_..._prompt, pq dai ja recebe o prompt e limpa


