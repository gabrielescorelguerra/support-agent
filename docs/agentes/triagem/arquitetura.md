# Arquitetura

## Visão geral

O modelo LLM recebe a mensagem do cliente e executa a triagem em dois passos:

1. **Identificação do caminho**
   - Define o departamento para o qual o cliente deve ser transferido e indica
     a confiança dessa solução.
   - Identifica, quando a mensagem permitir, o sistema, o equipamento e a
     situação.
   - Pode identificar fatores como o humor do cliente.
2. **Definição da resposta**
   - Com confiança suficiente, informa ao cliente que vai encaminhá-lo para o
     caminho definido, usando uma mensagem pré-definida.
   - Sem confiança suficiente, envia uma mensagem para obter as informações
     necessárias.
   - Mensagens simples e previsíveis podem ser escolhidas entre templates
     pré-definidos, com prevenção de repetição.
   - Respostas mais específicas podem ser geradas por outra LLM.

## Aspectos e vantagens

- O código pode ser reaproveitado para evoluir para sistemas mais complexos.
- Há mais controle sobre a qualidade das respostas, o custo e o fluxo.
- A solução fica livre de possíveis mudanças de preço no TiFlux.
  - Flutuações nos preços de LLM podem ser reduzidas trocando de modelo, por
    exemplo.
- Há mais possibilidades do que permanecer apenas no TiFlux:
  - começar o suporte partindo do problema informado na triagem;
  - identificar o humor do cliente e adaptar o atendimento;
  - guardar o histórico de interações passadas com o cliente.
- É possível usar uma LLM mais barata e economizar com mensagens pré-definidas.

## Componentes e integrações

O fluxo externo passa pelo WhatsApp e pelo TiFlux até o webhook da integração
de IA. Dentro da integração, o webhook encaminha a requisição ao roteador, que
aciona o agente de triagem e devolve a resposta ao TiFlux.

Os diagramas detalhados do fluxo geral e do agente estão em [Fluxo](./fluxo.md).

## Histórico e contexto do prompt

O histórico é construído pelo `ConversationStore` e passado aos agentes. Um
processador pode operar sobre o prompt completo, mas isso dificulta distinguir:

- instruções do sistema;
- histórico;
- mensagem atual;
- formato de saída.

Uma alternativa mais robusta é criar um objeto estruturado antes da montagem:

```python
class PromptContext(BaseModel):
    system_instructions: str
    history: list[str]
    current_message: str
    output_format: str
```

O pipeline de limpeza pode ser chamado dentro de cada agente e definido dentro
de suas próprias pastas. Uma boa localização é `build_..._prompt`, que já
recebe o prompt e pode limpá-lo.