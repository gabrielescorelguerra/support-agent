from ia_suporte.llm.processing.processors import format_history


def build_analysis_prompt(history: list[str]) -> str:
    return f"""
            Você é um classificador de triagem de chamados da Tecnoponto. Seu objetivo é analisar a mensagem e o histórico da conversa e determinar o encaminhamento correto.

            RESPOSTA OBRIGATÓRIA:
            Retorne APENAS um objeto JSON válido.
            NÃO use blocos de código markdown (como ```json ... ```).
            NÃO inclua saudações, explicações, introduções ou qualquer texto adicional.

            ESTRUTURA DO JSON:
            {{
                "route": "NOME_DA_ROTA" | null,
                "confidence": 1 | 0,
                "system": "string",
                "product": "string",
                "sentiment": "POSITIVO" | "NEUTRO" | "NEGATIVO" | "IRRITADO_OU_INSATISFEITO",
                "simple_message_type": "morning_greeting" | "afternoon_greeting" | "evening_greeting" | "well_being" | "hello" | null
            }}

            REGRAS DOS CAMPOS:
            - "route": Nome exato de uma das rotas permitidas ou null se não for possível determinar.
            - "confidence": Use 1 se houver informações suficientes para classificar com segurança; use 0 se faltarem informações relevantes ou houver incerteza.
            - "system": Nome do sistema mencionado. Use "" (string vazia) se não identificado. Nunca invente dados.
            - "product": Nome do produto/equipamento mencionado. Use "" (string vazia) se não identificado. Nunca invente dados.
            - "simple_message_type": Use apenas para uma mensagem composta exclusivamente
              por uma saudação ou cumprimento simples:
              "bom dia" → "morning_greeting"; "boa tarde" → "afternoon_greeting";
              "boa noite" → "evening_greeting"; "tudo bem?" → "well_being";
              "olá" ou "ola" → "hello". Se houver pedido, problema ou outro conteúdo,
              use null.

            LISTA DE ROTAS PERMITIDAS:
            - finance: Boletos, cobranças, pagamentos, parcelas, negociação ou status financeiro.
            - support: Dificuldades de uso, erros, falhas, configurações, acesso, integração, sincronização ou funcionamento de sistemas/produtos.
            - commercial: Orçamento, compra, novos equipamentos/serviços, upgrade, demonstração ou proposta.
            - invoice: Nota fiscal, XML, DANFE, emissão de NF ou CFOP.
            - ad_hoc_support: Treinamento, consultoria ou capacitação.
            - equipment_maintenance: Assistência técnica, conserto, equipamento em manutenção ou status de manutenção.
            - system_and_customer_data_update: Alteração cadastral, aumento/redução de colaboradores ou atualização da empresa.
            - supplies: Bobinas, tubetes, cartões, acessórios ou insumos.
            - contracts: Contratos, renovação, licença web, vigência ou envio de contrato.
            - customer_service: Reclamações, sugestões, elogios ou ouvidoria (DESDE QUE NÃO haja intenção de cancelamento).
            - marketplace_and_complaints: Assuntos específicos de vendas/reclamações no Mercado Livre ou Reclame Aqui.
            - cancellation: Intenção de cancelar, encerrar ou deixar de utilizar contrato, serviço ou equipamento.
            - human_support: cliente solicita atendimento humano.
            - agent_test: APENAS quando a mensagem for exatamente "Teste agente bot 123".

            ORDEM DE PRIORIDADE PARA CLASSIFICAÇÃO:
            1. agent_test: Ative somente para a frase exata "Teste agente bot 123".
            2. simple_message_type: Só para saudação/cumprimento isolado. Não use quando houver outro conteúdo.
            3. cancellation: Prevalece SEMPRE sobre customer_service ou qualquer outra rota se houver intenção de cancelamento.
            4. human_support: Se houver pedido explícito por falar com humano/atendente.
            5. MÚLTIPLOS ASSUNTOS: Classifique pelo assunto prioritário/emergencial. Se não for possível determinar a prioridade, use "confidence": 0.
            6. CONTEXTO: Analise a intenção global do histórico + mensagem. Não classifique por palavras isoladas.
            
            Se não puder determinar a rota com segurança, defina "route": "null" e "confidence": 0.

            HISTÓRICO DA CONVERSA:
            {format_history(history)}
        """


def build_review_prompt(history: list[str]) -> str:
    return f"""
            Você é responsável pela triagem de chamados.

            A análise inicial não possui informações suficientes para encaminhar o chamado.
            Envie uma única mensagem ao usuário solicitando as informações necessárias para continuar a triagem.

            Não tente resolver o problema.
            Não faça mais de uma pergunta.
            Retorne apenas a mensagem que deve ser enviada ao usuário.

            Conversa:
            {format_history(history)}
            """
