import os
import requests


class GeminiAPI:
    def __init__(self, base_url: str):
        """
        Initialize the GeminiAPI instance with a base URL. The API key is read from the environment.
        """
        self.base_url = base_url
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")

    def ask_question(self, question: str) -> str:
        """
        Sends a question to the Gemini API and returns the response.

        :param question: The question to send to the API.
        :return: The API's response as a string.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "question": question
            }
            response = requests.post(f"{self.base_url}/ask", json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("answer", "No answer provided by the API.")
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"
