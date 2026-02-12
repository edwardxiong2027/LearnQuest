"""
LearnQuest - K-12 Offline Tutoring Platform
Flask Backend Server
"""

import os
import sqlite3
from flask import Flask, g, send_from_directory

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('LEARNQUEST_DB', os.path.join(BASE_DIR, 'database', 'learnquest.db'))
CONTENT_DIR = os.environ.get('LEARNQUEST_CONTENT', os.path.join(BASE_DIR, 'content'))
PROMPTS_DIR = os.environ.get('LEARNQUEST_PROMPTS', os.path.join(BASE_DIR, 'prompts'))

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

app.secret_key = os.urandom(24)
app.config['DB_PATH'] = DB_PATH
app.config['CONTENT_DIR'] = CONTENT_DIR
app.config['PROMPTS_DIR'] = PROMPTS_DIR
app.config['LLM_MODEL'] = os.environ.get('LEARNQUEST_MODEL', 'phi3')


def get_db():
    """Get database connection for current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA journal_mode=OFF')
        g.db.execute('PRAGMA synchronous=OFF')
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database from schema. Creates new DB or updates existing one with new tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute('PRAGMA journal_mode=OFF')
    db.execute('PRAGMA synchronous=OFF')
    schema_path = os.path.join(BASE_DIR, 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        try:
            db.executescript(f.read())
        except sqlite3.OperationalError:
            pass  # Some tables may already exist
    db.close()


# Make get_db available to blueprints
app.get_db = get_db

# Register blueprints
from api.routes_auth import auth_bp
from api.routes_lessons import lessons_bp
from api.routes_quiz import quiz_bp
from api.routes_progress import progress_bp
from api.routes_teacher import teacher_bp
from api.routes_tutor import tutor_bp
from api.routes_math import math_bp
from api.routes_generate import generate_bp
from api.routes_flashcards import flashcards_bp
from api.routes_notes import notes_bp
from api.routes_bookmarks import bookmarks_bp
from api.routes_search import search_bp
from api.routes_worksheets import worksheets_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(lessons_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(progress_bp, url_prefix='/api/progress')
app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
app.register_blueprint(tutor_bp, url_prefix='/api/tutor')
app.register_blueprint(math_bp, url_prefix='/api/math')
app.register_blueprint(generate_bp, url_prefix='/api/generate')
app.register_blueprint(flashcards_bp, url_prefix='/api/flashcards')
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(worksheets_bp, url_prefix='/api')


@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    from api.routes_teacher import get_leaderboard as _get_lb
    return _get_lb()


@app.route('/api/daily-challenge', methods=['GET'])
def get_daily_challenge():
    from api.routes_progress import get_daily_challenge_handler
    return get_daily_challenge_handler()


@app.route('/api/daily-challenge/submit', methods=['POST'])
def submit_daily_challenge():
    from api.routes_progress import submit_daily_challenge_handler
    return submit_daily_challenge_handler()


@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    from api.routes_progress import get_vocabulary as _get_vocab
    return _get_vocab()


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('LEARNQUEST_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
