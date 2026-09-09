# # # EXEMPLO
# # triage_llm = GeminiClient()
# # response_llm = GroqClient()

# # triage_agent = TriageAgent(
# #     triage_llm=triage_llm,
# #     response_llm=response_llm
# # )

# # from .base import LLM

# from ia_suporte.agents.base import WebhookData
# from ia_suporte.agents.triage.agent import TriageAgent
# from ia_suporte.llm.gemini import GeminiLLM

# gemini_2_5_flash = GeminiLLM("gemini-3.1-flash-lite")
# gemini_3_1_flash = GeminiLLM("gemini-3.1-flash")

# data = WebhookData(
#     chat_id=123, name="Roberto", email="a@gmail.com", messages=["oi", "ok"]
# )

# triage_agent = TriageAgent(llm=gemini_2_5_flash, data=data)

# # if for pra triagem
# response = triage_agent.run()
# print(response)
