def build_analysis_prompt(history: str) -> str:
    return f"""
                Você é responsável pela triagem de chamados.
                Você é responsável pela triagem de chamados.

                Analise a conversa e determine o encaminhamento mais adequado.

                Você deve retornar APENAS um JSON válido, sem markdown, explicações ou texto adicional.

                O JSON deve seguir exatamente esta estrutura:

                {{
                    "route": "string ou null",
                    "confidence": 0,
                    "system": "string",
                    "product": "string"
                }}

                ### Campos

                - route: setor para o qual o chamado deve ser encaminhado.
                - confidence: nível de confiança da classificação. Use apenas:
                    - 1: existem informações suficientes para classificar e encaminhar o chamado.
                    - 0: faltam informações relevantes para determinar o encaminhamento.
                - system: sistema relacionado ao chamado. Se não for possível identificar, use "".
                - product: produto relacionado ao chamado. Se não for possível identificar, use "".

                ### Rotas disponíveis

                Escolha APENAS uma das seguintes opções para `route`:

                - "technical_support": problemas técnicos, erros, falhas, funcionamento do sistema ou produto.
                - "commercial": dúvidas sobre contratação, planos, preços, propostas ou vendas.
                - "financial": pagamentos, cobranças, boletos, faturas ou questões financeiras.
                - "other": assuntos que não se enquadram nas categorias anteriores.


                ### Histórico de conversa

                {history}
            """


def build_review_prompt(history: str) -> str:
    return f"""
            Você é responsável pela triagem de chamados.

            A análise inicial não possui informações suficientes para encaminhar o chamado.
            Envie uma única mensagem ao usuário solicitando as informações necessárias para continuar a triagem.

            Não tente resolver o problema.
            Não faça mais de uma pergunta.
            Retorne apenas a mensagem que deve ser enviada ao usuário.

            Conversa:
            {history}
            """
