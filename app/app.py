import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils.llm_api.gemini_api.gemini_api import ask_gemini  # Import your custom function

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = os.getenv("GEMINI_API")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'response': 'Please provide a message'}), 400

        # Use your custom function instead of the official SDK
        response = ask_gemini(user_message, GOOGLE_API_KEY)

        # Handle error responses from your custom function
        if response == "ERROR":
            return jsonify({'response': 'Failed to get response from Gemini API'}), 500

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)