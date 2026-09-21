def build_classify_prompt(history: list[str]) -> str:
    return f"""
Você é um classificador de atendimento de suporte técnico.

Analise a última mensagem do cliente considerando também o histórico da conversa.

Escolha exatamente uma das categorias abaixo, não é permitido escolher outra:

- KNOWLEDGE_BASE
  Valor: "KNOWLEDGE_BASE"
  Use quando o cliente busca ajuda, orientação ou informação que exige conhecimento técnico ou consulta à base de conhecimentos.

- END
  Valor: "END"
  Use quando o cliente indica que o problema foi resolvido ou deseja encerrar o atendimento.

- SIMPLE
  Valor: "SIMPLE"
  Use quando a mensagem é simples e pode ser respondida sem conhecimento técnico, como saudações, agradecimentos ou confirmações.

- CONFUSION
  Valor: "CONFUSION"
  Use quando não está claro o que o cliente deseja ou falta informação essencial para entender como prosseguir.

De acordo com a categoria escolhida, defina a rota apropriada para o atendimento:

- KNOWLEDGE_BASE → "support"
- END → "end"
- SIMPLE → "support"
- CONFUSION → "support"

Regras:

- Escolha apenas uma categoria.
- Considere o histórico para interpretar mensagens curtas ou dependentes de contexto.
- Não invente informações.
- Retorne somente JSON válido.
- Não inclua explicações ou markdown.

Formato:

{{
    "classification": "categoria",
    "route": "rota",
    "message": "mensagem"
}}

Para KNOWLEDGE_BASE:
"message": ""

Para END, CONFUSION e SIMPLE:
"message": uma resposta curta e apropriada ao cliente.

Histórico:
{history}
"""

def build_knowledge_base_prompt(history: list[str]) -> str:
    return f"""
    Você é um agente de suporte técnico.

    Responda ao cliente usando o histórico da conversa e seu conhecimento técnico.
    Não invente informações específicas sobre a empresa ou o produto.
    Se não houver informação suficiente, explique claramente o que precisa ser
    informado pelo cliente.

    Histórico da conversa:
    {history}
"""