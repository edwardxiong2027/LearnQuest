"""Notes system routes - CRUD for student notes."""

import datetime
from flask import Blueprint, request, jsonify, session, current_app

notes_bp = Blueprint('notes', __name__)


def get_db():
    return current_app.get_db()


@notes_bp.route('', methods=['GET'])
def list_notes():
    """List all notes for the current user."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    lesson_id = request.args.get('lesson_id')

    if lesson_id:
        rows = db.execute(
            'SELECT * FROM notes WHERE user_id = ? AND lesson_id = ? ORDER BY updated_at DESC',
            (session['user_id'], lesson_id)
        ).fetchall()
    else:
        rows = db.execute(
            'SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC LIMIT 50',
            (session['user_id'],)
        ).fetchall()

    return jsonify({'notes': [dict(r) for r in rows]})


@notes_bp.route('', methods=['POST'])
def create_note():
    """Create a new note."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    db = get_db()
    now = datetime.datetime.now().isoformat()

    db.execute(
        'INSERT INTO notes (user_id, lesson_id, lesson_title, subject, grade, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (session['user_id'], data.get('lesson_id'), data.get('lesson_title'),
         data.get('subject'), data.get('grade'), content, now, now)
    )
    db.commit()
    return jsonify({'message': 'Note saved'})


@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    db = get_db()
    now = datetime.datetime.now().isoformat()

    db.execute(
        'UPDATE notes SET content = ?, updated_at = ? WHERE id = ? AND user_id = ?',
        (content, now, note_id, session['user_id'])
    )
    db.commit()
    return jsonify({'message': 'Note updated'})


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    db.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, session['user_id']))
    db.commit()
    return jsonify({'message': 'Note deleted'})
