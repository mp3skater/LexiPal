# gemini_api.py
import requests
import os


def ask_gemini(question, api_key):
    """
    Sends a question to the Gemini API and returns the response.

    :param question: The question to send to Gemini.
    :param api_key: Your API key for the Gemini service.
    :return: The response content from Gemini.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
