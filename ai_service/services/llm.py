import random

def chat(system_prompt: str, user_message: str, json_mode: bool = False) -> str:
    """
    Stub LLM — returns realistic fake responses.
    Replace this with real OpenAI call when you have an API key:

    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
    """

    # Detect what kind of prompt this is and return appropriate stub
    prompt_lower = system_prompt.lower()

    if "email analysis" in prompt_lower or "analyze" in prompt_lower:
        return _email_analysis_stub(user_message)

    elif "intent" in prompt_lower or "classify" in prompt_lower:
        return _intent_stub(user_message)

    elif "reply" in prompt_lower or "email writer" in prompt_lower:
        return _reply_stub(user_message)

    elif "workflow" in prompt_lower and "json" in prompt_lower:
        return _workflow_stub(user_message)

    elif "extract" in prompt_lower or "social media content" in prompt_lower:
        return _social_extract_stub(user_message)

    elif "adapt" in prompt_lower or "copywriter" in prompt_lower:
        return _social_adapt_stub(system_prompt, user_message)

    else:
        return '{"result": "stub response", "status": "ok"}'


def _email_analysis_stub(text: str) -> str:
    return '''{
        "summary": "The sender is requesting information about your services and pricing.",
        "sentiment": "positive",
        "priority": "medium",
        "key_points": [
            "Interested in your product",
            "Asking about pricing",
            "Wants a demo"
        ]
    }'''


def _intent_stub(text: str) -> str:
    text_lower = text.lower()

    if any(word in text_lower for word in ["meeting", "schedule", "call", "appointment"]):
        intent = "meeting_request"
    elif any(word in text_lower for word in ["complaint", "angry", "frustrated", "issue", "problem"]):
        intent = "complaint"
    elif any(word in text_lower for word in ["urgent", "asap", "immediately", "emergency"]):
        intent = "urgent"
    else:
        intent = "general"

    return f'''{{
        "intent": "{intent}",
        "confidence": 0.92,
        "reasoning": "Based on the keywords and context in the message."
    }}'''


def _reply_stub(text: str) -> str:
    return '''{
        "reply": "Thank you for reaching out. I have received your message and will get back to you shortly. If you have any urgent queries, please don't hesitate to follow up.",
        "subject": "Re: Your inquiry"
    }'''


def _workflow_stub(text: str) -> str:
    return '''{
        "name": "AI Generated Workflow",
        "trigger_type": "api.trigger",
        "trigger_config": {},
        "steps": [
            {
                "step_type": "ai",
                "action": "ai.analyze_email",
                "config": {},
                "order": 1,
                "on_failure": "stop"
            },
            {
                "step_type": "ai",
                "action": "ai.generate_reply",
                "config": {"tone": "professional"},
                "order": 2,
                "on_failure": "stop"
            }
        ]
    }'''


def _social_extract_stub(text: str) -> str:
    return '''{
        "topic": "product launch",
        "tone": "excited",
        "key_points": [
            "New product is live",
            "Game changing features",
            "Available now"
        ],
        "call_to_action": "Try it today"
    }'''


def _social_adapt_stub(system_prompt: str, text: str) -> str:
    prompt_lower = system_prompt.lower()

    if "twitter" in prompt_lower:
        return '''{
            "adapted_text": "Big news! Synthetix OS is LIVE — the AI automation platform that works like a digital employee. Try it today! #AI #Automation #Productivity #SynthetixOS",
            "hashtags": ["#AI", "#Automation", "#Productivity", "#SynthetixOS"],
            "character_count": 148
        }'''

    elif "linkedin" in prompt_lower:
        return '''{
            "adapted_text": "Today marks a significant milestone for our team.\\n\\nWe are thrilled to announce the launch of Synthetix OS — an AI-powered automation platform that acts as a digital employee for your business.\\n\\nInstead of spending hours on repetitive tasks, Synthetix OS handles them autonomously using intelligent AI agents.\\n\\nThis is just the beginning. We are excited about what lies ahead.\\n\\n#AI #Automation #ProductLaunch #SynthetixOS",
            "hashtags": ["#AI", "#Automation", "#ProductLaunch", "#SynthetixOS"],
            "character_count": 487
        }'''

    elif "instagram" in prompt_lower:
        return '''{
            "adapted_text": "Something big just dropped and we could not be more excited to share it with you.\\n\\nSynthetix OS is here — your AI-powered digital employee that automates everything so you can focus on what matters.\\n\\nLink in bio to try it free!",
            "hashtags": ["#AI", "#Automation", "#Tech", "#ProductLaunch", "#SynthetixOS", "#DigitalEmployee", "#AItools"],
            "character_count": 234
        }'''

    else:
        return '''{
            "adapted_text": "Excited to announce the launch of Synthetix OS! Check it out.",
            "hashtags": ["#AI", "#Automation"],
            "character_count": 62
        }'''