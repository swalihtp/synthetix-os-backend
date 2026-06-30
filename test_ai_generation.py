import requests

BASE = "http://localhost:8000/api"

# Login
res = requests.post(
    f"{BASE}/auth/login/",
    json={
        "email": "swalihmhdtp@gmail.com",
        "password": "pas@1234",
    },
)
token = res.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

prompts = [
    {
        "name": "Meeting Bot",
        "prompt": "When someone emails asking for a meeting, schedule it and notify me on Telegram",
    },
    {
        "name": "Social Bot",
        "prompt": "Post my content across all social media platforms",
    },
    {
        "name": "Alert Bot",
        "prompt": "When I get an urgent email notify me on Telegram immediately",
    },
]

for p in prompts:
    print(f"\nGenerating: {p['name']}")
    print(f"Prompt: {p['prompt']}")

    res = requests.post(f"{BASE}/agent/generate/", headers=headers, json=p)

    if res.status_code == 201:
        data = res.json()
        wf = data["workflow"]
        print(f"✅ Created: {wf['name']}")
        print(f"   Trigger: {wf['trigger_type']}")
        print(f"   Steps: {wf['steps_count']}")
        for step in wf["steps"]:
            print(f"   {step['order']}. {step['action']}")
    else:
        print(f"❌ Failed: {res.text}")


{
    "trigger": {
        "type": "scheduled",
        "pipeline": {
            "stages": [
                {"name": "ingestion", "tasks": ["fetch_html", "fetch_rss"]},
                {"name": "processing", "tasks": ["clean_text", "extract_entities"]},
                {
                    "name": "intelligence",
                    "tasks": [
                        "compare_with_history",
                        "detect_changes",
                        "cluster_topics",
                    ],
                },
                {"name": "reasoning", "tasks": ["llm_insight_generation"]},
                {"name": "output", "tasks": ["generate_report", "publish"]},
            ]
        },
        "schedule": "0 9 * * *",
        "timezone": "Asia/Kolkata",
    }
}
