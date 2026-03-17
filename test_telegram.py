import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Token: {TOKEN[:20]}...")
print(f"Chat ID: {CHAT_ID}")

response = httpx.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": "✅ <b>Synthetix OS Test</b>\n\nTelegram integration is working!",
        "parse_mode": "HTML",
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")