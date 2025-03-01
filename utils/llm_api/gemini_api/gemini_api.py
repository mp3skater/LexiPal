# gemini_api.py
import requests


def ask_gemini(question: str, api_key: str) -> str:
    """
    Sends a question to the Gemini API and returns the response text or "ERROR".

    :param question: The question to send to Gemini.
    :param api_key: Your API key for the Gemini service.
    :return: The extracted response text or "ERROR" if any failure occurs.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Attempt to extract the answer text
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "ERROR"

    except requests.exceptions.RequestException:
        return "ERROR"
