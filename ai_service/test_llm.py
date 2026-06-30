from services.llm_service import llm

print("start")

response = llm.invoke("Say hello")

print(response)
