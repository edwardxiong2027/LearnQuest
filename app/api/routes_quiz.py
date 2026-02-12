"""Quiz routes - serving quizzes, submitting answers, scoring."""

import os
import json
import datetime
from flask import Blueprint, request, jsonify, session, current_app

quiz_bp = Blueprint('quiz', __name__)


def get_db():
    return current_app.get_db()


@quiz_bp.route('/<unit_id>', methods=['GET'])
def get_quiz(unit_id):
    """Get quiz questions for a unit."""
    subject = request.args.get('subject')
    grade = request.args.get('grade', type=int)

    if not subject or grade is None:
        return jsonify({'error': 'subject and grade parameters required'}), 400

    content_dir = current_app.config['CONTENT_DIR']
    grade_str = 'k' if grade == 0 else str(grade)
    filepath = os.path.join(content_dir, subject, f'{grade_str}.json')

    if not os.path.exists(filepath):
        return jsonify({'error': 'Content not found'}), 404

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Find the unit
    for unit in data.get('units', []):
        if unit['id'] == unit_id:
            quiz = unit.get('unit_quiz', {})
            return jsonify({
                'unit_id': unit_id,
                'title': f"{unit['title']} Quiz",
                'questions': quiz.get('questions', []),
                'passing_score': quiz.get('passing_score', 70),
                'xp_reward': quiz.get('xp_reward', 50),
                'badge': quiz.get('badge', None)
            })

    return jsonify({'error': 'Unit not found'}), 404


@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and record results."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    quiz_id = data.get('quiz_id')
    subject = data.get('subject')
    grade = data.get('grade')
    score = data.get('score', 0)
    total_questions = data.get('total_questions', 0)
    correct_answers = data.get('correct_answers', 0)
    time_spent = data.get('time_spent_seconds', 0)
    answers = data.get('answers', [])

    db = get_db()
    user_id = session['user_id']

    # Record quiz result
    db.execute(
        '''INSERT INTO quiz_results
           (user_id, quiz_id, subject, grade, score, total_questions, correct_answers, time_spent_seconds, answers_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, quiz_id, subject, grade, score, total_questions, correct_answers, time_spent, json.dumps(answers))
    )

    xp_award = 0
    badges_earned = []
    passing_score = 70

    if score >= passing_score:
        xp_award = 50
        if score == 100:
            xp_award += 25
            # Perfect score badge
            _award_badge(db, user_id, 'perfect_score', 'Perfect Score', 'Get 100% on a quiz')
            badges_earned.append('perfect_score')

        # Speed badge
        if time_spent > 0 and time_spent < 120 and total_questions >= 5:
            _award_badge(db, user_id, 'speed_demon', 'Speed Demon', 'Complete a quiz in under 2 minutes')
            badges_earned.append('speed_demon')

        # First quiz badge
        quiz_count = db.execute(
            'SELECT COUNT(*) as cnt FROM quiz_results WHERE user_id = ? AND score >= 70',
            (user_id,)
        ).fetchone()['cnt']
        if quiz_count <= 1:
            _award_badge(db, user_id, 'first_quiz', 'Quiz Taker', 'Complete your first quiz')
            badges_earned.append('first_quiz')

        db.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (xp_award, user_id))

        # Update level
        from api.routes_lessons import calculate_level
        user = db.execute('SELECT xp FROM users WHERE id = ?', (user_id,)).fetchone()
        new_level = calculate_level(user['xp'])
        db.execute('UPDATE users SET level = ? WHERE id = ?', (new_level, user_id))

    db.commit()

    return jsonify({
        'message': 'Quiz submitted',
        'score': score,
        'passed': score >= passing_score,
        'xp_awarded': xp_award,
        'badges_earned': badges_earned
    })


@quiz_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """AI-generate a quiz (placeholder — requires LLM)."""
    return jsonify({'error': 'Quiz generation requires AI tutor to be running'}), 503


def _award_badge(db, user_id, badge_id, badge_name, badge_desc):
    """Award a badge if not already earned."""
    existing = db.execute(
        'SELECT id FROM badges WHERE user_id = ? AND badge_id = ?',
        (user_id, badge_id)
    ).fetchone()
    if not existing:
        db.execute(
            'INSERT INTO badges (user_id, badge_id, badge_name, badge_description) VALUES (?, ?, ?, ?)',
            (user_id, badge_id, badge_name, badge_desc)
        )
