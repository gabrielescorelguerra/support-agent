Simula webhook usando polling

Quando há mensagens enviadas, chama router, enviando uma simulação do payload do TiFlux

Da para transformar mensagens grandes em streams - gabriel routes_secullumia.py

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

departamento ta errado, ta indo o do futuro, nao o que
pegar o do futuro pelo campo personalizado e mudar url de post