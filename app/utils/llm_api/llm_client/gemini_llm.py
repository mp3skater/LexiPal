import requests
from typing import List, Dict
from app.utils.llm_api.llm_client.base_llm import BaseLLMClient


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def query(self, system_prompt: str, user_inputs: List[str]) -> List[Dict]:
        results = []
        headers = {'Content-Type': 'application/json'}
        url = f"{self.base_url}?key={self.api_key}"

        for idx, user_input in enumerate(user_inputs, 1):
            payload = {
                "contents": [{
                    "parts": [{"text": user_input}]
                }]
            }

            # Add system instruction if provided
            if system_prompt.strip():
                payload["systemInstruction"] = {
                    "parts": [{"text": system_prompt}]
                }

            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                try:
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    metadata = {
                        'model': self.model,
                        'safety_ratings': data['candidates'][0].get('safetyRatings', []),
                        'finish_reason': data['candidates'][0].get('finishReason', '')
                    }
                except (KeyError, IndexError):
                    content = "ERROR"
                    metadata = {"error": "Failed to parse API response"}

            except requests.exceptions.RequestException as e:
                content = "ERROR"
                metadata = {"error": str(e)}

            results.append({
                'id': f'request{idx}',
                'response': content,
                'metadata': metadata
            })

        return results
