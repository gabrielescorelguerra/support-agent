# define o pipeline de sanitizacoes a serem feitas
# ordem importa

# class PromptPipeline:
#     def __init__(self, processors: list[PromptProcessor]) -> None:
#         self.processors = processors

#     def process(self, prompt: str) -> str:
#         for processor in self.processors:
#             prompt = processor.process(prompt)
#         return prompt

# Bom chamar em -> GeminiLLM.generate(), antes de chamar a LLM de fato, preserva agentes e pode ficar igual para todos os provedores
# deve-se executar ele antes do retry, dai separa em outra funcao o retry]

# dai o LLM registry poderia montar o pipeline
# def build_prompt_pipeline() -> PromptPipeline:
    # return PromptPipeline(
    #     processors=[
    #         NormalizeWhitespace(),
    #         RemoveDuplicateMessages(),
    #         LimitHistory(max_characters=12000),
    #         RedactSensitiveData(),
    #     ]
    # )

# por exemplo
# "gemini": lambda model: GeminiLLM(
#     model=model,
#     api_key=config.gemini_api_key,
#     prompt_pipeline=build_prompt_pipeline(),
# )