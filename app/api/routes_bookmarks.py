"""Bookmark system routes."""

from flask import Blueprint, request, jsonify, session, current_app

bookmarks_bp = Blueprint('bookmarks', __name__)


def get_db():
    return current_app.get_db()


@bookmarks_bp.route('', methods=['GET'])
def list_bookmarks():
    """List all bookmarks for the current user."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    rows = db.execute(
        'SELECT * FROM bookmarks WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()

    return jsonify({'bookmarks': [dict(r) for r in rows]})


@bookmarks_bp.route('/toggle', methods=['POST'])
def toggle_bookmark():
    """Toggle a bookmark on/off for a lesson."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    lesson_id = data.get('lesson_id')
    if not lesson_id:
        return jsonify({'error': 'lesson_id required'}), 400

    db = get_db()
    user_id = session['user_id']

    existing = db.execute(
        'SELECT id FROM bookmarks WHERE user_id = ? AND lesson_id = ?',
        (user_id, lesson_id)
    ).fetchone()

    if existing:
        db.execute('DELETE FROM bookmarks WHERE id = ?', (existing['id'],))
        db.commit()
        return jsonify({'bookmarked': False})
    else:
        db.execute(
            'INSERT INTO bookmarks (user_id, lesson_id, lesson_title, subject, grade) VALUES (?, ?, ?, ?, ?)',
            (user_id, lesson_id, data.get('lesson_title', ''), data.get('subject', ''), data.get('grade'))
        )
        db.commit()
        return jsonify({'bookmarked': True})


@bookmarks_bp.route('/check/<lesson_id>', methods=['GET'])
def check_bookmark(lesson_id):
    """Check if a lesson is bookmarked."""
    if 'user_id' not in session:
        return jsonify({'bookmarked': False})

    db = get_db()
    existing = db.execute(
        'SELECT id FROM bookmarks WHERE user_id = ? AND lesson_id = ?',
        (session['user_id'], lesson_id)
    ).fetchone()

    return jsonify({'bookmarked': bool(existing)})
