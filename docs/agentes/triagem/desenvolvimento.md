# Desenvolvimento

## Pendências funcionais

- Corrigir o departamento encaminhado: atualmente pode estar indo para o
  departamento do futuro, e não para o departamento correto.
- Obter o departamento do futuro pelo campo personalizado.
- Alterar a URL usada no POST.
- Simular o webhook usando polling.
- Quando houver mensagens enviadas, chamar o router enviando uma simulação do
  payload do TiFlux.
- Avaliar a transformação de mensagens grandes em streams, conforme a
  referência `gabriel routes_secullumia.py`.

## Plano de implementação

### 1. Consolidar o funcionamento
- [x] Implementar simulação do webhook do TiFlux por meio do telegram
- [x] Implementar roteamento básico
- [ ] Refinar geração de respostas
	- [ ] Detecção de *small-talking*, retomada de tópicos mencionados
	- [ ] Favorecer *caching*
	- [ ] Implementar templates para casos simples, com escolha aleatória e prevenção de repetições
	- [ ] Refinar chamada à LLM em caso de necessidade de diagnóstico
- [ ] Identificação de fatores como humor, sistema, equipamento... e persistência deles para uso futuro
### 2. Testar durante a implementação

Adicionar testes junto com cada etapa, cobrindo casos normais, ambíguos,
múltiplas intenções, falhas da LLM, JSON inválido, rotas desconhecidas e
webhooks duplicados. Usar casos reais anonimizados para medir precisão,
falsos encaminhamentos e confiança.

### 3. Instrumentar a operação

- [ ] Adicionar logs estruturados, métricas, tracing, health checks e alertas.
- [ ] Registrar rota, confiança, duração, erro e resultado sem expor dados sensíveis.

### 4. Endurecer segurança e confiabilidade

- [ ] Autenticar o webhook
- [ ] Definir como lidar com dados sensíveis
	- [ ] PII redacting
- [ ] Proteger e rotacionar segredos
- [ ] Configurar timeouts e retries limitados
- [ ] Edempotência, controle de concorrência, fila e fallback humano.

### 5. Fazer deploy controlado

Preparar persistência, backup e migrações; configurar Docker/CI-CD e HTTPS;
validar em staging com casos anonimizados; acompanhar métricas em produção e
manter rollback disponível.

## Possibilidades futuras

- Gerenciamento externo de prompts e otimização automática