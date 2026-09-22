# Testes e qualidade

## Cobertura mínima

- Casos normais de cada rota.
- Mensagens ambíguas.
- Mensagens com múltiplas intenções.
- Solicitação explícita de atendimento humano.
- Intenção de cancelamento concorrendo com reclamação ou SAC.
- Mensagens simples e previsíveis.
- Necessidade de formular pergunta de esclarecimento.
- Falha da LLM.
- JSON inválido ou rota desconhecida.
- Webhooks duplicados.

## Avaliação

Criar um conjunto de casos reais anonimizados para medir:

- precisão da classificação;
- falsos encaminhamentos;
- confiança informada pelo modelo;
- qualidade das perguntas de esclarecimento;
- repetição e adequação das mensagens;
- duração e taxa de erro por etapa.

Os testes devem ser escritos durante a implementação, e não apenas antes do
deploy. Alterações locais pendentes e o teste removido anteriormente devem ser
revisados antes da publicação.

## Operação

Além dos testes automatizados, usar logs estruturados, métricas, tracing,
health checks, alertas e rastreabilidade por atendimento para acompanhar o
comportamento em produção.