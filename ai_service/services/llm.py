import json



def chat(system_prompt: str, user_message: str, json_mode: bool = False) -> str:
    prompt_lower = system_prompt.lower()

    # IMPORTANT: workflow check must come FIRST before email analysis
    if "workflow automation expert" in prompt_lower or (
        "workflow" in prompt_lower and "trigger" in prompt_lower
    ):
        return _workflow_stub(user_message)

    elif "email analysis" in prompt_lower:
        return _email_analysis_stub(user_message)

    elif "intent" in prompt_lower or "classify" in prompt_lower:
        return _intent_stub(user_message)

    elif "reply" in prompt_lower or "email writer" in prompt_lower:
        return _reply_stub(user_message)

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
        "reply": "Thank you for reaching out. I have received your message and will get back to you shortly. If you have any urgent queries, please do not hesitate to follow up.",
        "subject": "Re: Your inquiry"
    }'''


def _workflow_stub(text: str) -> str:
    text_lower = text.lower()

    # Meeting related
    if any(word in text_lower for word in ["meeting", "schedule", "calendar", "appointment"]):
        return '''{
            "name": "Auto Meeting Scheduler",
            "trigger_type": "gmail.email_received",
            "trigger_config": {},
            "steps": [
                {"step_type": "system", "action": "gmail.fetch_email", "config": {}, "order": 1, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.detect_meeting_intent", "config": {}, "order": 2, "on_failure": "stop"},
                {"step_type": "system", "action": "calendar.check_availability", "config": {"days_ahead": 7}, "order": 3, "on_failure": "stop"},
                {"step_type": "system", "action": "calendar.create_event", "config": {"duration_minutes": 30}, "order": 4, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.generate_reply", "config": {"tone": "friendly"}, "order": 5, "on_failure": "stop"},
                {"step_type": "system", "action": "gmail.send_reply", "config": {}, "order": 6, "on_failure": "continue"},
                {"step_type": "system", "action": "system.notify_user", "config": {"channel": "telegram"}, "order": 7, "on_failure": "continue"}
            ]
        }'''

    # Email reply related
    elif any(word in text_lower for word in ["email", "reply", "respond", "inbox"]):
        return '''{
            "name": "Smart Email Responder",
            "trigger_type": "gmail.email_received",
            "trigger_config": {},
            "steps": [
                {"step_type": "system", "action": "gmail.fetch_email", "config": {}, "order": 1, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.analyze_email", "config": {}, "order": 2, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.classify_intent", "config": {"detect": ["meeting_request", "complaint", "general", "urgent"]}, "order": 3, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.generate_reply", "config": {"tone": "professional"}, "order": 4, "on_failure": "stop"},
                {"step_type": "system", "action": "gmail.send_reply", "config": {}, "order": 5, "on_failure": "continue"},
                {"step_type": "system", "action": "system.notify_user", "config": {"channel": "telegram"}, "order": 6, "on_failure": "continue"}
            ]
        }'''

    # Social media related
    elif any(word in text_lower for word in ["social", "twitter", "linkedin", "instagram", "post", "content"]):
        return '''{
            "name": "Social Media Scheduler",
            "trigger_type": "api.trigger",
            "trigger_config": {},
            "steps": [
                {"step_type": "ai", "action": "ai.extract_content", "config": {}, "order": 1, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.adapt_twitter", "config": {"platform": "twitter", "max_chars": 280}, "order": 2, "on_failure": "continue"},
                {"step_type": "ai", "action": "ai.adapt_linkedin", "config": {"platform": "linkedin"}, "order": 3, "on_failure": "continue"},
                {"step_type": "ai", "action": "ai.adapt_instagram", "config": {"platform": "instagram"}, "order": 4, "on_failure": "continue"},
                {"step_type": "system", "action": "system.schedule_posts", "config": {"platforms": ["twitter", "linkedin", "instagram"]}, "order": 5, "on_failure": "stop"},
                {"step_type": "system", "action": "system.notify_user", "config": {"channel": "telegram"}, "order": 6, "on_failure": "continue"}
            ]
        }'''

    # Notification / alert related
    elif any(word in text_lower for word in ["notify", "alert", "telegram", "notification"]):
        return '''{
            "name": "Email Alert System",
            "trigger_type": "gmail.email_received",
            "trigger_config": {},
            "steps": [
                {"step_type": "system", "action": "gmail.fetch_email", "config": {}, "order": 1, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.classify_intent", "config": {"detect": ["urgent", "complaint", "general"]}, "order": 2, "on_failure": "stop"},
                {"step_type": "system", "action": "system.notify_user", "config": {"channel": "telegram"}, "order": 3, "on_failure": "stop"}
            ]
        }'''

    # Default
    else:
        return '''{
            "name": "Custom Workflow",
            "trigger_type": "api.trigger",
            "trigger_config": {},
            "steps": [
                {"step_type": "ai", "action": "ai.analyze_email", "config": {}, "order": 1, "on_failure": "stop"},
                {"step_type": "ai", "action": "ai.generate_reply", "config": {"tone": "professional"}, "order": 2, "on_failure": "stop"},
                {"step_type": "system", "action": "system.notify_user", "config": {"channel": "telegram"}, "order": 3, "on_failure": "continue"}
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
            "adapted_text": "Today marks a significant milestone for our team.\\n\\nWe are thrilled to announce the launch of Synthetix OS — an AI-powered automation platform that acts as a digital employee for your business.\\n\\nInstead of spending hours on repetitive tasks, Synthetix OS handles them autonomously using intelligent AI agents.\\n\\n#AI #Automation #ProductLaunch #SynthetixOS",
            "hashtags": ["#AI", "#Automation", "#ProductLaunch", "#SynthetixOS"],
            "character_count": 487
        }'''
    elif "instagram" in prompt_lower:
        return '''{
            "adapted_text": "Something big just dropped and we could not be more excited to share it with you.\\n\\nSynthetix OS is here — your AI-powered digital employee that automates everything so you can focus on what matters.\\n\\nLink in bio to try it free!",
            "hashtags": ["#AI", "#Automation", "#Tech", "#ProductLaunch", "#SynthetixOS"],
            "character_count": 234
        }'''
    else:
        return '''{
            "adapted_text": "Excited to announce the launch of Synthetix OS! Check it out.",
            "hashtags": ["#AI", "#Automation"],
            "character_count": 62
        }'''