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

# GOOGLE_API_KEY = os.getenv("GEMINI_API")
GOOGLE_API_KEY = os.getenv("GEMINI_PRO_API")


# Server-side conversation storage and locks
conversations = {}
conversation_locks = defaultdict(Lock)

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/languages')
def languages():
    return render_template('languages.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat_interface():
    return render_template('chat.html')

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
            # Extract persona directly from "with [X]" (avoids generating new names)
            f"Based on the user's input: '{user_input}', extract the **exact name** of the persona they want to talk to (after 'with'). Use 1-3 words. Examples: 'Diego Maradona', NOT 'Reporter' or 'Giovanni Rossi'.",
            # Casual opener FROM the persona's perspective (not the user's)
            f"Generate a creative (can make details up), casual, not superficial but not too long first message in the specified language AS THE PERSONA. Not markdown. only thing allowed is html strong tags for actions. Example for Maradona: Nessuno mi ha detto sapevo che la mia intervistatrice sarebbe cosi bella. <strong>winks</strong> Che vuoi chiedermi bella?",
            # Descriptive chat title highlighting the persona
            f"Summarise the info generated. Example: 'User impersonates good looking interviewer interviewing Maradona after a game. Maradona says the interviewer may start asking questions.'"
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

            # In the /chat route's chat_questions
            chat_questions = [
                f"Respond as \"{conversation['persona']}\" to: history: \"{conversation['history']}\" | Current question: \"{user_message}\"",
                f"Create a concise new summary of this conversation including: \"{conversation['summary']}\" and the Current question: \"{user_message}\"",
                # Single f-string for review question
                (
                    f"Analyze this language message: '{user_message}'. Give feedback in {conversation['persona']}'s language. Format EXACTLY:\n"
                    "• Grammar: [c.a. 3 sentences assessment with reason]\n"
                    "• Vocabulary: [1 sentence assessment]\n"
                    "• Possible Correction: [correction ONLY if needed]\n"
                    "Use • bullets. Max 100 words. Example:\n"
                    "• Grammar: Incorrect verb conjugation 'were'. Should be 'was'. Because it is a singular noun.\n"
                    "• Vocabulary: 'hey' is informal and colloquial. Acceptable in this conversation. OR 'wassup man' is informal and highly colloquial. Not acceptable in this conversation.\n"
                    "• Possible Correction: 'I go' → 'I went' OR No correction needed"
                )
            ]

            answers, raw_response = ask_questions(chat_questions, GOOGLE_API_KEY)


            if len(answers) != 3:
                error_msg = f"Invalid chat response. Expected 3 answers, got {len(answers)}. Raw response: {raw_response}"
                return jsonify({'response': error_msg}), 400

            conversation['summary'] = answers[1]
            conversation['history'].append({
                'user': user_message,
                'bot': answers[0]
            })

        return jsonify({
            'response': answers[0],
            'persona': conversation['persona'],
            'review': answers[2]  # Add review to response
        })

    except Exception as e:
        return jsonify({'response': f'Chat error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
