def email_analysis_prompt() -> str:
    return """You are an email analysis assistant.
Analyze the given email and return a JSON object with:
- summary: one sentence summary of the email
- sentiment: positive, negative, or neutral
- priority: high, medium, or low
- key_points: list of main points
Return only valid JSON."""


def intent_detection_prompt(detect: list) -> str:
    intents = ", ".join(detect)
    return f"""You are an intent classification assistant.
Classify the given text into one of these intents: {intents}.
Return a JSON object with:
- intent: the detected intent (must be one of: {intents})
- confidence: float between 0 and 1
- reasoning: one sentence explanation
Return only valid JSON."""


def reply_generation_prompt(tone: str) -> str:
    return f"""You are a professional email writer.
Generate a {tone} email reply based on the original email and detected intent.
Return a JSON object with:
- reply: the full email reply text
- subject: suggested reply subject line
Return only valid JSON."""


def workflow_generation_prompt() -> str:
    return """You are a workflow automation expert.
Convert the user's natural language goal into a structured workflow JSON.
Available triggers: gmail.email_received, webhook.received, api.trigger, schedule.cron
Available actions: ai.analyze_email, ai.classify_intent, ai.generate_reply, 
                   ai.extract_content, ai.adapt_twitter, ai.adapt_linkedin,
                   ai.adapt_instagram, gmail.send_reply, gmail.fetch_email,
                   calendar.check_availability, calendar.create_event,
                   slack.send_message, telegram.send_message,
                   system.schedule_posts, system.notify_user

Return a JSON object with:
- name: workflow name
- trigger_type: one trigger from the list above
- trigger_config: dict of trigger settings
- steps: list of steps, each with:
    - step_type: "ai" or "system"
    - action: one action from the list above
    - config: dict of action settings
    - order: integer starting from 1
    - on_failure: "stop" or "continue"
Return only valid JSON."""


def social_extract_prompt() -> str:
    return """You are a social media content strategist.
Analyze the given text and extract:
Return a JSON object with:
- topic: main topic in 3 words max
- tone: excited, professional, casual, or informative
- key_points: list of 3 key messages
- call_to_action: suggested CTA
Return only valid JSON."""


def social_adapt_prompt(platform: str) -> str:
    limits = {
        "twitter": "280 characters max, punchy, use hashtags",
        "linkedin": "professional tone, up to 3000 characters, paragraph format",
        "instagram": "casual and visual, caption style, heavy hashtags at end",
    }
    rule = limits.get(platform, "general social media post")
    return f"""You are a social media copywriter for {platform}.
Adapt the given content for {platform}: {rule}.
Return a JSON object with:
- adapted_text: the platform-specific post text
- hashtags: list of relevant hashtags
- character_count: length of adapted_text
Return only valid JSON."""