# import re
# import json
# import requests
# from dotenv import load_dotenv
# import os

# load_dotenv()

# OPENROUTER_API_KEY = os.getenv('OPEN_ROUTER_API_KEY')


# class AgentPlanner:

#     def __init__(self):
#         self.base_url = "http://localhost:11434/api/generate"
#         self.model = "llama3"  # change if needed

#     def generate_plan(self, user_prompt: str) -> dict:

#         system_prompt = """
#             You are an automation planner.

#             Convert the user instruction into EXACTLY this JSON schema:

#             {
#                 "trigger": {
#                     "tool": "<tool_name>",
#                     "event": "<event_name>",
#                     "config": {}
#                 },
#                 "actions": [
#                     {
#                         "tool": "<tool_name>",
#                         "action": "<action_name>",
#                         "config": {}
#                     }
#                 ]
#             }

#             Rules:
#             - Use ONLY these tools:
#               gmail, google_calendar, google_sheets, telegram
#             - Do NOT nest fields.
#             - Do NOT create extra keys.
#             - Always include "config" even if empty.
#             - Return ONLY valid JSON. No explanation. No markdown.
#             """

#         full_prompt = f"""
#         {system_prompt}

#         USER INSTRUCTION:
#         {user_prompt}
#         """


#         response = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "x-ai/grok-4.1-fast",
#                 "messages": [
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt},
#                 ],
#                 "temperature": 0.1
#             },
#         )

#         if response.status_code != 200:
#             raise Exception(f"OpenRouter Error: {response.text}")

#         result = response.json()

#         try:
#             content = result["choices"][0]["message"]["content"]
#         except (KeyError, IndexError):
#             raise Exception(f"Unexpected OpenRouter response: {result}")

#         return extract_json(content)
    




# def extract_json(text: str) -> dict:
#     """
#     Extract the first JSON object from LLM response safely.
#     """

#     # Remove markdown code blocks
#     text = re.sub(r"```json", "", text)
#     text = re.sub(r"```", "", text)

#     # Remove comments (// style)
#     text = re.sub(r"//.*", "", text)

#     # Extract JSON object
#     match = re.search(r"\{.*\}", text, re.DOTALL)

#     if not match:
#         raise ValueError("No JSON object found in LLM response")

#     json_str = match.group()

#     return json.loads(json_str)