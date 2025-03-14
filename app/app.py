import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from threading import Lock
from collections import defaultdict
from utils.multiple_questions_handler.handler import ask_questions
from utils.logging_handler.handler import logger

# Apply logging decorator if enabled
ask_questions = logger.log_questions(ask_questions)

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

GOOGLE_API_KEY = os.getenv("GEMINI_API")

# Server-side conversation storage and locks
conversations = {}
conversation_locks = defaultdict(Lock)

@app.route('/')
def home():
    return render_template('start.html')  # Changed from index.html

# Add new route for the chat interface
@app.route('/chat')
def chat_interface():
    return render_template('index.html')  # Serve index.html here

@app.route('/start', methods=['POST'])
def start_chat():
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        user_input = data.get('message', '').strip()

        if not conversation_id:
            return jsonify({'response': 'Missing conversation ID'}), 400
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

        with conversation_locks[conversation_id]:
            conversations[conversation_id] = {
                'persona': answers[0],
                'active': True,
                'summary': answers[2],
                'history': []
            }

        return jsonify({
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
        user_message = data.get('message', '').strip()

        if not conversation_id:
            return jsonify({'response': 'Missing conversation ID'}), 400
        if not user_message:
            return jsonify({'response': 'Empty message'}), 400

        with conversation_locks[conversation_id]:
            conversation = conversations.get(conversation_id)
            if not conversation or not conversation.get('active'):
                return jsonify({'response': 'Invalid conversation ID or session not active'}), 400

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

        return jsonify({
            'response': answers[0],
            'persona': conversation['persona']
        })

    except Exception as e:
        return jsonify({'response': f'Chat error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
