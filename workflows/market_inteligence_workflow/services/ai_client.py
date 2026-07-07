import requests
import os
from dotenv import load_dotenv
load_dotenv()
class AIClient:

    def __init__(self):

        self.base_url = f"{os.getenv('AI_SERVICE_URL')}/api"

        self.timeout = 300

    def execute(
        self,
        task,
        payload,
    ):
        
        payload = {
            "task":task,
            "payload":payload
        }

        print(f"PAYLOAD: {payload}")
        
        response = requests.post(
            f"{self.base_url}/execute",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()


ai_client = AIClient()
