import os
import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils.multiple_questions_handler.handler import ask_questions  # Import your method

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Toggle logging on/off with this one line
LOGGING_ENABLED = False  # Set to False to disable logging

# In-memory store for conversations (Not persistent)
conversations = {}

GOOGLE_API_KEY = os.getenv("GEMINI_API")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_chat():
    try:
        data = request.json
        conversation_id = data.get('conversation_id') or str(uuid.uuid4())
        user_input = data.get('message', '').strip()

        if not user_input:
            return jsonify({'response': 'Please specify who, language, and topic'}), 400

        setup_questions = [
            f"Based on '{user_input}', create a 1-3 word name for the AI persona",
            f"Generate a starting message in the specified language from this persona about the topic",
            f"Create a short chat description including: {user_input}"
        ]

        answers, raw_response = ask_questions(setup_questions, GOOGLE_API_KEY)

        if len(answers) != 3:
            error_msg = f"Invalid setup response. Expected 3 answers, got {len(answers)}. Raw response: {raw_response}"
            return jsonify({'response': error_msg}), 400

        conversations[conversation_id] = {
            'persona': answers[0],
            'active': True,
            'summary': answers[2],
            'history': []
        }

        # Logging
        if LOGGING_ENABLED:
            print(f"🟢 New Conversation Started (ID: {conversation_id})")
            print(f"   User Input: {user_input}")
            print(f"   AI Persona: {answers[0]}")
            print(f"   AI First Response: {answers[1]}")

        return jsonify({
            'conversation_id': conversation_id,
            'response': answers[1],
            'persona': answers[0]
        })

    except Exception as e:
        return jsonify({'response': f'Chat initialization failed: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        if not conversation_id or conversation_id not in conversations:
            return start_chat()

        conversation = conversations[conversation_id]
        if not conversation.get('active'):
            return jsonify({'response': 'Start a conversation first'}), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'response': 'Empty message'}), 400

        chat_questions = [
            f"Respond as {conversation['persona']} to: {user_message}",
            f"Create a concise new summary of this conversation including: {conversation['summary']} and {user_message}"
        ]

        answers, raw_response = ask_questions(chat_questions, GOOGLE_API_KEY)

        if len(answers) != 2:
            error_msg = f"Invalid chat response. Expected 2 answers, got {len(answers)}. Raw response: {raw_response}"
            return jsonify({'response': error_msg}), 400

        conversation['summary'] = answers[1]
        conversation['history'].append({
            'user': user_message,
            'bot': answers[0]
        })

        # Logging
        if LOGGING_ENABLED:
            print(f"📝 Conversation ID: {conversation_id}")
            print(f"   User: {user_message}")
            print(f"   AI: {answers[0]}")

        return jsonify({
            'response': answers[0],
            'persona': conversation['persona']
        })

    except Exception as e:
        return jsonify({'response': f'Chat error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
