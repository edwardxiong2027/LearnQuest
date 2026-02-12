"""Progress tracking, badges, leaderboard, daily challenges."""

import os
import json
import random
import datetime
from flask import Blueprint, request, jsonify, session, current_app

progress_bp = Blueprint('progress', __name__)


def get_db():
    return current_app.get_db()


@progress_bp.route('/<int:student_id>', methods=['GET'])
def get_progress(student_id):
    """Get student progress summary."""
    db = get_db()

    # Subject breakdown
    subjects = {}
    for subject in ['math', 'science', 'ela', 'social_studies']:
        row = db.execute(
            '''SELECT COUNT(*) as completed,
                      AVG(score) as avg_score
               FROM lesson_progress
               WHERE user_id = ? AND subject = ? AND completed = 1''',
            (student_id, subject)
        ).fetchone()

        # Count total lessons available
        content_dir = current_app.config['CONTENT_DIR']
        user = db.execute('SELECT grade FROM users WHERE id = ?', (student_id,)).fetchone()
        grade = user['grade'] if user else 3
        grade_str = 'k' if grade == 0 else str(grade)
        filepath = os.path.join(content_dir, subject, f'{grade_str}.json')
        total = 0
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                for unit in data.get('units', []):
                    total += len(unit.get('lessons', []))

        subjects[subject] = {
            'completed': row['completed'] if row else 0,
            'total': max(total, 1),
            'avg_score': row['avg_score'] if row else None
        }

    total_lessons = db.execute(
        'SELECT COUNT(*) as cnt FROM lesson_progress WHERE user_id = ? AND completed = 1',
        (student_id,)
    ).fetchone()['cnt']

    total_quizzes = db.execute(
        'SELECT COUNT(*) as cnt FROM quiz_results WHERE user_id = ? AND score >= 70',
        (student_id,)
    ).fetchone()['cnt']

    return jsonify({
        'subjects': subjects,
        'total_lessons': total_lessons,
        'total_quizzes': total_quizzes
    })


@progress_bp.route('/badges', methods=['GET'])
def get_badges():
    """Get all available badges and which ones the user has earned."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    earned = db.execute(
        'SELECT badge_id, badge_name, badge_description, earned_at FROM badges WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()

    return jsonify({
        'earned': [dict(b) for b in earned]
    })


def get_daily_challenge_handler():
    """Get today's daily challenge."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']
    today = datetime.date.today().isoformat()

    # Check if already completed
    existing = db.execute(
        'SELECT * FROM daily_challenges WHERE user_id = ? AND challenge_date = ?',
        (user_id, today)
    ).fetchone()

    if existing and existing['completed_at']:
        return jsonify({'completed': True, 'correct': existing['correct']})

    if existing:
        return jsonify({
            'completed': False,
            'subject': existing['subject'],
            'question': json.loads(existing['question_json'])
        })

    # Generate a new challenge
    user = db.execute('SELECT grade FROM users WHERE id = ?', (user_id,)).fetchone()
    grade = user['grade'] if user else 3

    challenge = _generate_daily_challenge(grade)
    if not challenge:
        return jsonify({'error': 'No challenge available'}), 404

    db.execute(
        'INSERT INTO daily_challenges (user_id, challenge_date, subject, question_json) VALUES (?, ?, ?, ?)',
        (user_id, today, challenge['subject'], json.dumps(challenge['question']))
    )
    db.commit()

    return jsonify({
        'completed': False,
        'subject': challenge['subject'],
        'question': challenge['question']
    })


def submit_daily_challenge_handler():
    """Submit daily challenge answer."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']
    today = datetime.date.today().isoformat()
    data = request.get_json()
    answer = data.get('answer')

    challenge = db.execute(
        'SELECT * FROM daily_challenges WHERE user_id = ? AND challenge_date = ?',
        (user_id, today)
    ).fetchone()

    if not challenge:
        return jsonify({'error': 'No challenge found'}), 404

    if challenge['completed_at']:
        return jsonify({'error': 'Already completed'}), 400

    question = json.loads(challenge['question_json'])

    # Check answer
    correct = False
    correct_answer = None
    if question.get('type') == 'multiple_choice':
        correct = answer == question.get('correct')
        correct_answer = question['options'][question['correct']] if 'options' in question else ''
    else:
        correct_answer = str(question.get('answer', ''))
        correct = str(answer).strip().lower() == correct_answer.lower()

    xp_award = 15 if correct else 0

    db.execute(
        'UPDATE daily_challenges SET answer = ?, correct = ?, completed_at = ? WHERE user_id = ? AND challenge_date = ?',
        (str(answer), correct, datetime.datetime.now().isoformat(), user_id, today)
    )

    if xp_award > 0:
        db.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (xp_award, user_id))
        from api.routes_lessons import calculate_level
        user = db.execute('SELECT xp FROM users WHERE id = ?', (user_id,)).fetchone()
        db.execute('UPDATE users SET level = ? WHERE id = ?', (calculate_level(user['xp']), user_id))

        # Daily challenge badge
        from api.routes_quiz import _award_badge
        _award_badge(db, user_id, 'daily_challenger', 'Challenge Accepted', 'Complete a daily challenge')

    db.commit()

    return jsonify({
        'correct': correct,
        'correct_answer': correct_answer,
        'xp_awarded': xp_award
    })


@progress_bp.route('/vocabulary', methods=['GET'])
def get_vocabulary():
    """Get vocabulary words from completed lessons."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']
    user = db.execute('SELECT grade FROM users WHERE id = ?', (user_id,)).fetchone()
    grade = user['grade'] if user else 3
    subject_filter = request.args.get('subject')

    # Get completed lesson IDs
    completed = db.execute(
        'SELECT lesson_id, subject FROM lesson_progress WHERE user_id = ? AND completed = 1',
        (user_id,)
    ).fetchall()

    content_dir = current_app.config['CONTENT_DIR']
    grade_str = 'k' if grade == 0 else str(grade)
    words = []

    subjects = [subject_filter] if subject_filter else ['math', 'science', 'ela', 'social_studies']
    completed_ids = {row['lesson_id'] for row in completed}

    for subject in subjects:
        filepath = os.path.join(content_dir, subject, f'{grade_str}.json')
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        for unit in data.get('units', []):
            for lesson in unit.get('lessons', []):
                if lesson.get('id') not in completed_ids:
                    continue
                vocab = lesson.get('content', {}).get('key_vocabulary', [])
                for word in vocab:
                    words.append({
                        'word': word,
                        'subject': subject,
                        'lesson_id': lesson.get('id', ''),
                        'lesson_title': lesson.get('title', '')
                    })

    # Deduplicate
    seen = set()
    unique_words = []
    for w in words:
        if w['word'].lower() not in seen:
            seen.add(w['word'].lower())
            unique_words.append(w)

    return jsonify({'words': unique_words})


def _generate_daily_challenge(grade):
    """Generate a random daily challenge question."""
    subjects = ['math', 'science', 'ela', 'social_studies']
    subject = random.choice(subjects)

    content_dir = current_app.config['CONTENT_DIR']
    grade_str = 'k' if grade == 0 else str(grade)
    filepath = os.path.join(content_dir, subject, f'{grade_str}.json')

    if not os.path.exists(filepath):
        # Try math as fallback
        filepath = os.path.join(content_dir, 'math', f'{grade_str}.json')
        subject = 'math'
        if not os.path.exists(filepath):
            return None

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Collect all practice problems
    problems = []
    for unit in data.get('units', []):
        for lesson in unit.get('lessons', []):
            for prob in lesson.get('practice_problems', []):
                problems.append(prob)

    if not problems:
        return None

    question = random.choice(problems)
    return {'subject': subject, 'question': question}
