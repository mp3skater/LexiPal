import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from threading import Lock
from collections import defaultdict
from utils.multiple_questions_handler.handler import ask_questions
from utils.logging_handler.handler import logger
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask import flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required


app = Flask(__name__)
# Add these configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    google_api_key = db.Column(db.String(100))
    google_pro_api_key = db.Column(db.String(100))
    past_chats = db.Column(db.JSON, default=list)

    def __repr__(self):
        return f"User('{self.email}', '{self.name}')"

# Apply logging decorator if enabled
ask_questions = logger.log_questions(ask_questions)

CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

GOOGLE_API_KEY = os.getenv("GEMINI_PRO_API") or os.getenv("GEMINI_API")

# Server-side conversation storage and locks
conversations = {}
conversation_locks = defaultdict(Lock)

@app.route('/languages')
def languages():
    return render_template('languages.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if user:
        # Add password reset logic here
        flash('Password reset link sent to your email', 'success')
    else:
        flash('No account found with that email', 'danger')

    return redirect(url_for('login'))

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        google_api_key = request.form.get('google_api_key')
        google_pro_api_key = request.form.get('google_pro_api_key')

        # Validation
        if not all([email, name, password, confirm_password]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create user
        new_user = User(
            email=email,
            name=name,
            password=hashed_password,
            google_api_key=google_api_key,
            google_pro_api_key=google_pro_api_key
        )
        db.session.add(new_user)
        db.session.commit()

        # Send welcome email
        send_welcome_email(new_user)

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


def send_welcome_email(user):
    return
    msg = Message('Welcome to Lexipal',
                  sender='noreply@lexipal.com',
                  recipients=[user.email])
    msg.body = f'''Hi {user.name},

Welcome to Lexipal! Your account has been successfully created.

Features:
- Store multiple API keys
- Access chat history
- Language learning tools

Happy learning!'''
    mail.send(msg)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
