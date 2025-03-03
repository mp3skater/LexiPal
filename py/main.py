from py.utils.llm_api.gemini_api.gemini_api import ask_gemini
from browser import document, html, alert
import os
import json
import requests  # Brython's built-in requests

API_KEY = "AIzaSyDv_ybEhpBuUu76uxDKuH9KsW0yp_VR5qQ"


def create_message_element(text, is_user=False):
    """Create styled chat message elements"""
    div = html.DIV(Class="ai-msg bg-gray-100 p-3 rounded")
    if is_user:
        div.className = "user-msg bg-blue-100 p-3 rounded ml-8"
    div.text = f"You: {text}" if is_user else f"LexiPal: {text}"
    return div


def handle_gemini_response(user_input, response):
    """Process Gemini API response and update chat"""
    try:
        response_json = response.json()
        if 'candidates' not in response_json:
            raise Exception("Invalid API response")

        gemini_text = response_json['candidates'][0]['content']['parts'][0]['text']
        display_message(user_input, gemini_text)

    except Exception as e:
        alert(f"Error processing response: {str(e)}")


def display_message(user_input, ai_response):
    """Add messages to chat history"""
    chat_div = document["chat_history"]

    # Add user message
    chat_div <= create_message_element(user_input, is_user=True)

    # Add AI response
    chat_div <= create_message_element(ai_response)

    # Clear input and scroll to bottom
    document["user_input"].value = ""
    chat_div.scrollTop = chat_div.scrollHeight


def send_to_gemini(event):
    """Handle message sending"""
    user_input = document["user_input"].value.strip()
    if not user_input:
        alert("Please enter a message!")
        return

    try:
        # Show loading state
        btn = document["send_btn"]
        btn.text = "Sending..."
        btn.classList.add("opacity-50", "cursor-not-allowed")

        # Make API request
        response = ask_gemini(user_input, )
        response.raise_for_status()
        handle_gemini_response(user_input, response)

    except Exception as e:
        alert(f"API Error: {str(e)}")
    finally:
        # Reset button
        btn.text = "Send"
        btn.classList.remove("opacity-50", "cursor-not-allowed")


# Event listeners
document["send_btn"].bind("click", send_to_gemini)


# Handle Enter key (but allow Shift+Enter for new lines)
def handle_keypress(event):
    if event.key == "Enter" and not event.shiftKey:
        event.preventDefault()
        send_to_gemini(None)


document["user_input"].bind("keypress", handle_keypress)
