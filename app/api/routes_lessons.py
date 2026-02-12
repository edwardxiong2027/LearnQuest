"""Lesson and curriculum content routes."""

import os
import json
from flask import Blueprint, request, jsonify, session, current_app

lessons_bp = Blueprint('lessons', __name__)


def get_db():
    return current_app.get_db()


def load_curriculum_file(subject, grade):
    """Load a grade's curriculum JSON file."""
    content_dir = current_app.config['CONTENT_DIR']
    grade_str = 'k' if grade == 0 else str(grade)
    filepath = os.path.join(content_dir, subject, f'{grade_str}.json')
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        return json.load(f)


@lessons_bp.route('/curriculum', methods=['GET'])
def get_curriculum():
    """Get the master curriculum map."""
    content_dir = current_app.config['CONTENT_DIR']
    filepath = os.path.join(content_dir, 'curriculum_map.json')
    if not os.path.exists(filepath):
        return jsonify({'error': 'Curriculum map not found'}), 404
    with open(filepath, 'r') as f:
        data = json.load(f)
    return jsonify(data)


@lessons_bp.route('/curriculum/<subject>/<int:grade>', methods=['GET'])
def get_subject_grade(subject, grade):
    """Get all units for a subject and grade."""
    data = load_curriculum_file(subject, grade)
    if not data:
        return jsonify({'error': f'Content not found for {subject} grade {grade}'}), 404

    # Attach completion status if user is logged in
    if 'user_id' in session:
        db = get_db()
        completed = db.execute(
            'SELECT lesson_id FROM lesson_progress WHERE user_id = ? AND completed = 1',
            (session['user_id'],)
        ).fetchall()
        completed_ids = set(row['lesson_id'] for row in completed)

        for unit in data.get('units', []):
            for lesson in unit.get('lessons', []):
                lesson['completed'] = lesson['id'] in completed_ids

    return jsonify(data)


@lessons_bp.route('/lesson/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get a specific lesson by ID."""
    subject = request.args.get('subject')
    grade = request.args.get('grade', type=int)

    if not subject or grade is None:
        return jsonify({'error': 'subject and grade parameters required'}), 400

    data = load_curriculum_file(subject, grade)
    if not data:
        return jsonify({'error': 'Content not found'}), 404

    # Find the lesson
    for unit in data.get('units', []):
        for lesson in unit.get('lessons', []):
            if lesson['id'] == lesson_id:
                return jsonify(lesson)

    return jsonify({'error': 'Lesson not found'}), 404


@lessons_bp.route('/lesson/<lesson_id>/complete', methods=['POST'])
def complete_lesson(lesson_id):
    """Mark a lesson as complete and award XP."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    subject = data.get('subject')
    grade = data.get('grade')
    score = data.get('score', 0)

    db = get_db()
    user_id = session['user_id']

    import datetime

    # Upsert lesson progress
    existing = db.execute(
        'SELECT id, completed FROM lesson_progress WHERE user_id = ? AND lesson_id = ?',
        (user_id, lesson_id)
    ).fetchone()

    if existing and existing['completed']:
        return jsonify({'message': 'Already completed', 'xp_awarded': 0})

    if existing:
        db.execute(
            'UPDATE lesson_progress SET completed = 1, score = ?, completed_at = ?, attempts = attempts + 1 WHERE id = ?',
            (score, datetime.datetime.now().isoformat(), existing['id'])
        )
    else:
        db.execute(
            'INSERT INTO lesson_progress (user_id, lesson_id, subject, grade, completed, score, attempts, completed_at) VALUES (?, ?, ?, ?, 1, ?, 1, ?)',
            (user_id, lesson_id, subject, grade, score, datetime.datetime.now().isoformat())
        )

    # Award XP if passing score
    xp_award = 0
    if score >= 70:
        xp_award = 20
        if score == 100:
            xp_award += 10  # bonus for perfect
        db.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (xp_award, user_id))

        # Update level
        user = db.execute('SELECT xp FROM users WHERE id = ?', (user_id,)).fetchone()
        new_level = calculate_level(user['xp'])
        db.execute('UPDATE users SET level = ? WHERE id = ?', (new_level, user_id))

    db.commit()

    return jsonify({'message': 'Lesson completed', 'xp_awarded': xp_award})


def calculate_level(xp):
    """Calculate level from XP."""
    levels = [
        0, 50, 120, 200, 300, 420, 560, 720, 900, 1100,
        1320, 1560, 1820, 2100, 2400, 2720, 3060, 3420, 3800, 4200,
        4620, 5060, 5520, 6000, 6500, 7020, 7560, 8120, 8700, 9300,
        9920, 10560, 11220, 11900, 12600, 13320, 14060, 14820, 15600, 16400,
        17220, 18060, 18920, 19800, 20700, 21620, 22560, 23520, 24500, 25000
    ]
    level = 1
    for i, threshold in enumerate(levels):
        if xp >= threshold:
            level = i + 1
    return level
