import os
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from utils.multiple_questions_handler.handler import ask_questions  # Import your method

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

GOOGLE_API_KEY = os.getenv("GEMINI_API")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_chat():
    try:
        session.clear()

        # Generate chat context using your method
        setup_questions = [
            "Create a 1-3 word long name for who the AI will interpret",
            "Create a short starting message (1-2 sentences)",
            "Create a short description of the chat (including the starting message)"
        ]

        answers, raw_response = ask_questions(setup_questions, GOOGLE_API_KEY)

        # Validate answer count strictly
        if len(answers) != len(setup_questions):
            error_msg = f"Answer count mismatch. Expected {len(setup_questions)}, got {len(answers)}. Raw response: {raw_response}"
            return jsonify({'response': error_msg}), 400

        session.update({
            'persona': answers[0],
            'starting_message': answers[1],
            'description': answers[2],
            'summary': None,
            'history': []
        })

        return jsonify({
            'response': "With who, in what language and about what would you like to talk about?",
            'persona': session['persona']
        })

    except Exception as e:
        return jsonify({'response': f'Chat initialization failed: {str(e)}'}), 500


@app.route('/chat', methods=['POST'])
def chat():
    try:
        if 'summary' not in session:
            return jsonify({'response': 'Start a conversation first'}), 400

        data = request.json
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'response': 'Empty message'}), 400

        # Get current context
        current_summary = session['summary'] or session['description']

        # Generate response and new summary
        chat_questions = [
            f"Generate response using this context: {current_summary} + user message: {user_message}",
            "Create a concise new summary for future context"
        ]

        answers, raw_response = ask_questions(chat_questions, GOOGLE_API_KEY)

        # Validate answer count
        if len(answers) != len(chat_questions):
            error_msg = f"Failed to process message. Expected {len(chat_questions)} answers, got {len(answers)}. Raw response: {raw_response}"
            return jsonify({'response': error_msg}), 400

        # Update session state
        session['summary'] = answers[1]
        session['history'].append({
            'user': user_message,
            'bot': answers[0]
        })

        return jsonify({
            'response': answers[0],
            'persona': session['persona']
        })

    except Exception as e:
        return jsonify({'response': f'Chat error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)