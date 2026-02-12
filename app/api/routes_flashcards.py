"""Flashcard system routes with Leitner spaced repetition."""

import json
import datetime
from flask import Blueprint, request, jsonify, session, current_app

flashcards_bp = Blueprint('flashcards', __name__)


def get_db():
    return current_app.get_db()


@flashcards_bp.route('', methods=['GET'])
def list_flashcards():
    """List flashcards, optionally filtered by subject/grade."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']
    subject = request.args.get('subject')
    grade = request.args.get('grade')

    query = 'SELECT f.*, fp.box, fp.next_review, fp.times_correct, fp.times_wrong FROM flashcards f LEFT JOIN flashcard_progress fp ON f.id = fp.flashcard_id AND fp.user_id = ? WHERE f.user_id = ?'
    params = [user_id, user_id]

    if subject:
        query += ' AND f.subject = ?'
        params.append(subject)
    if grade:
        query += ' AND f.grade = ?'
        params.append(int(grade))

    query += ' ORDER BY f.created_at DESC'
    rows = db.execute(query, params).fetchall()

    return jsonify({'flashcards': [dict(r) for r in rows]})


@flashcards_bp.route('', methods=['POST'])
def create_flashcard():
    """Create a custom flashcard."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    db = get_db()
    user_id = session['user_id']

    front = data.get('front', '').strip()
    back = data.get('back', '').strip()
    if not front or not back:
        return jsonify({'error': 'Front and back are required'}), 400

    db.execute(
        'INSERT INTO flashcards (user_id, subject, grade, topic, front, back, hint, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, data.get('subject', ''), data.get('grade'), data.get('topic', ''),
         front, back, data.get('hint', ''), 'manual')
    )
    db.commit()
    return jsonify({'message': 'Flashcard created'})


@flashcards_bp.route('/study', methods=['GET'])
def get_study_cards():
    """Get flashcards due for review (Leitner algorithm)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']
    today = datetime.date.today().isoformat()
    subject = request.args.get('subject')

    # Cards with no progress entry (new cards) or due for review
    query = '''
        SELECT f.*, COALESCE(fp.box, 1) as box
        FROM flashcards f
        LEFT JOIN flashcard_progress fp ON f.id = fp.flashcard_id AND fp.user_id = ?
        WHERE f.user_id = ?
        AND (fp.next_review IS NULL OR fp.next_review <= ?)
    '''
    params = [user_id, user_id, today]

    if subject:
        query += ' AND f.subject = ?'
        params.append(subject)

    query += ' ORDER BY COALESCE(fp.box, 1) ASC, f.created_at ASC LIMIT 20'
    rows = db.execute(query, params).fetchall()

    return jsonify({'cards': [dict(r) for r in rows]})


@flashcards_bp.route('/review', methods=['POST'])
def review_flashcard():
    """Record a flashcard review result and advance/reset Leitner box."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    db = get_db()
    user_id = session['user_id']
    flashcard_id = data.get('flashcard_id')
    correct = data.get('correct', False)

    if not flashcard_id:
        return jsonify({'error': 'flashcard_id required'}), 400

    # Get current progress
    existing = db.execute(
        'SELECT * FROM flashcard_progress WHERE user_id = ? AND flashcard_id = ?',
        (user_id, flashcard_id)
    ).fetchone()

    now = datetime.datetime.now().isoformat()

    if existing:
        box = existing['box']
        if correct:
            new_box = min(box + 1, 5)
            db.execute(
                'UPDATE flashcard_progress SET box = ?, next_review = ?, last_reviewed = ?, times_correct = times_correct + 1 WHERE user_id = ? AND flashcard_id = ?',
                (new_box, _next_review_date(new_box), now, user_id, flashcard_id)
            )
        else:
            db.execute(
                'UPDATE flashcard_progress SET box = 1, next_review = ?, last_reviewed = ?, times_wrong = times_wrong + 1 WHERE user_id = ? AND flashcard_id = ?',
                (_next_review_date(1), now, user_id, flashcard_id)
            )
    else:
        new_box = 2 if correct else 1
        db.execute(
            'INSERT INTO flashcard_progress (user_id, flashcard_id, box, next_review, last_reviewed, times_correct, times_wrong) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, flashcard_id, new_box, _next_review_date(new_box), now, 1 if correct else 0, 0 if correct else 1)
        )

    db.commit()
    return jsonify({'message': 'Review recorded', 'correct': correct})


@flashcards_bp.route('/<int:card_id>', methods=['DELETE'])
def delete_flashcard(card_id):
    """Delete a flashcard."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    db.execute('DELETE FROM flashcard_progress WHERE flashcard_id = ? AND user_id = ?', (card_id, session['user_id']))
    db.execute('DELETE FROM flashcards WHERE id = ? AND user_id = ?', (card_id, session['user_id']))
    db.commit()
    return jsonify({'message': 'Deleted'})


def _next_review_date(box):
    """Calculate next review date based on Leitner box number."""
    # Box 1: 1 day, Box 2: 2 days, Box 3: 4 days, Box 4: 8 days, Box 5: 16 days
    days = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
    delta = days.get(box, 1)
    return (datetime.date.today() + datetime.timedelta(days=delta)).isoformat()
