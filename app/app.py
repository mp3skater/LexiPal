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
        data = request.json
        user_input = data.get('message', '').strip()

        if not user_input:
            return jsonify({'response': 'Please specify who, language, and topic'}), 400

        # Generate chat context based on user's initial input
        setup_questions = [
            f"Based on '{user_input}', create a 1-3 word name for the AI persona",
            f"Generate a starting message in the specified language from this persona about the topic",
            f"Create a short chat description including: {user_input}"
        ]

        answers, raw_response = ask_questions(setup_questions, GOOGLE_API_KEY)

        if len(answers) != 3:
            error_msg = f"Invalid setup response. Expected 3 answers, got {len(answers)}. Raw response: {raw_response}"
            return jsonify({'response': error_msg}), 400

        session.update({
            'persona': answers[0],
            'active': True,
            'summary': answers[2],  # Use description as initial summary
            'history': []
        })

        return jsonify({
            'response': answers[1],  # The generated starting message
            'persona': session['persona']
        })

    except Exception as e:
        return jsonify({'response': f'Chat initialization failed: {str(e)}'}), 500


@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not session.get('active'):
            return jsonify({'response': 'Start a conversation first'}), 400

        data = request.json
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'response': 'Empty message'}), 400

        # Generate response and update summary
        chat_questions = [
            f"Respond as {session['persona']} to: {user_message}",
            f"Create a concise new summary of this conversation including: {session['summary']} and {user_message}"
        ]

        answers, raw_response = ask_questions(chat_questions, GOOGLE_API_KEY)

        if len(answers) != 2:
            error_msg = f"Invalid chat response. Expected 2 answers, got {len(answers)}. Raw response: {raw_response}"
            return jsonify({'response': error_msg}), 400

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