"""Teacher dashboard routes - student management, reports, settings, export."""

import io
import csv
import json
from flask import Blueprint, request, jsonify, session, current_app, Response

teacher_bp = Blueprint('teacher', __name__)


def get_db():
    return current_app.get_db()


def require_teacher(f):
    """Decorator to require teacher role."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        db = get_db()
        user = db.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        if not user or user['role'] != 'teacher':
            return jsonify({'error': 'Teacher access required'}), 403
        return f(*args, **kwargs)
    return decorated


@teacher_bp.route('/students', methods=['GET'])
@require_teacher
def list_students():
    db = get_db()
    students = db.execute(
        'SELECT id, name, grade, xp, level, streak_days, last_active, created_at FROM users WHERE role = ? ORDER BY name',
        ('student',)
    ).fetchall()
    return jsonify({'students': [dict(s) for s in students]})


@teacher_bp.route('/report/<int:student_id>', methods=['GET'])
@require_teacher
def student_report(student_id):
    db = get_db()
    student = db.execute('SELECT * FROM users WHERE id = ? AND role = ?', (student_id, 'student')).fetchone()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Subject progress
    progress = []
    for subject in ['math', 'science', 'ela', 'social_studies']:
        row = db.execute(
            '''SELECT COUNT(*) as completed, AVG(score) as avg_score
               FROM lesson_progress WHERE user_id = ? AND subject = ? AND completed = 1''',
            (student_id, subject)
        ).fetchone()
        progress.append({
            'subject': subject,
            'completed': row['completed'],
            'avg_score': row['avg_score']
        })

    # Recent quizzes
    quizzes = db.execute(
        '''SELECT quiz_id, subject, score, total_questions, correct_answers, completed_at
           FROM quiz_results WHERE user_id = ? ORDER BY completed_at DESC LIMIT 20''',
        (student_id,)
    ).fetchall()

    # Badges
    badges = db.execute(
        'SELECT badge_id, badge_name, badge_description, earned_at FROM badges WHERE user_id = ?',
        (student_id,)
    ).fetchall()

    return jsonify({
        'student': dict(student),
        'progress': progress,
        'quizzes': [dict(q) for q in quizzes],
        'badges': [dict(b) for b in badges]
    })


@teacher_bp.route('/student/<int:student_id>', methods=['PUT'])
@require_teacher
def update_student(student_id):
    """Update a student's info."""
    db = get_db()
    student = db.execute('SELECT * FROM users WHERE id = ? AND role = ?', (student_id, 'student')).fetchone()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    name = data.get('name', student['name'])
    grade = data.get('grade', student['grade'])
    avatar = data.get('avatar', student['avatar'])

    if data.get('pin'):
        db.execute('UPDATE users SET name = ?, pin = ?, grade = ?, avatar = ? WHERE id = ?',
                   (name, data['pin'], grade, avatar, student_id))
    else:
        db.execute('UPDATE users SET name = ?, grade = ?, avatar = ? WHERE id = ?',
                   (name, grade, avatar, student_id))
    db.commit()
    return jsonify({'message': 'Student updated'})


@teacher_bp.route('/student/<int:student_id>', methods=['DELETE'])
@require_teacher
def delete_student(student_id):
    """Delete a student and all related data."""
    db = get_db()
    student = db.execute('SELECT * FROM users WHERE id = ? AND role = ?', (student_id, 'student')).fetchone()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Cascade delete all related data
    db.execute('DELETE FROM lesson_progress WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM quiz_results WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM badges WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM chat_history WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM daily_challenges WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM generated_content WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM flashcard_progress WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM flashcards WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM notes WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM bookmarks WHERE user_id = ?', (student_id,))
    db.execute('DELETE FROM users WHERE id = ?', (student_id,))
    db.commit()
    return jsonify({'message': 'Student deleted'})


@teacher_bp.route('/network-info', methods=['GET'])
@require_teacher
def network_info():
    """Return local network URL for classroom mode."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = '127.0.0.1'

    import os
    port = int(os.environ.get('LEARNQUEST_PORT', 5001))
    url = f'http://{ip}:{port}'
    return jsonify({'ip': ip, 'port': port, 'url': url})


@teacher_bp.route('/settings', methods=['GET'])
@require_teacher
def get_settings():
    db = get_db()
    settings = db.execute('SELECT key, value FROM settings').fetchall()
    result = {}
    for s in settings:
        result[s['key']] = s['value']
    return jsonify(result)


@teacher_bp.route('/settings', methods=['POST'])
@require_teacher
def update_settings():
    data = request.get_json()
    db = get_db()
    for key, value in data.items():
        db.execute(
            'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?',
            (key, str(value), str(value))
        )
    db.commit()
    return jsonify({'message': 'Settings updated'})


@teacher_bp.route('/export', methods=['POST'])
@require_teacher
def export_csv():
    db = get_db()
    students = db.execute(
        'SELECT id, name, grade, xp, level, streak_days FROM users WHERE role = ? ORDER BY name',
        ('student',)
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Grade', 'XP', 'Level', 'Streak', 'Math Lessons', 'Science Lessons', 'ELA Lessons', 'Social Studies Lessons', 'Quizzes Passed'])

    for student in students:
        row = [student['name'], student['grade'], student['xp'], student['level'], student['streak_days']]
        for subject in ['math', 'science', 'ela', 'social_studies']:
            cnt = db.execute(
                'SELECT COUNT(*) as cnt FROM lesson_progress WHERE user_id = ? AND subject = ? AND completed = 1',
                (student['id'], subject)
            ).fetchone()['cnt']
            row.append(cnt)
        quiz_cnt = db.execute(
            'SELECT COUNT(*) as cnt FROM quiz_results WHERE user_id = ? AND score >= 70',
            (student['id'],)
        ).fetchone()['cnt']
        row.append(quiz_cnt)
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=learnquest_progress.csv'}
    )


@teacher_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Public leaderboard (check if enabled)."""
    db = get_db()
    setting = db.execute("SELECT value FROM settings WHERE key = 'leaderboard_enabled'").fetchone()
    if setting and setting['value'] != 'true':
        return jsonify({'leaderboard': [], 'disabled': True})

    students = db.execute(
        'SELECT id, name, xp, level, streak_days FROM users WHERE role = ? ORDER BY xp DESC LIMIT 50',
        ('student',)
    ).fetchall()
    return jsonify({'leaderboard': [dict(s) for s in students]})


# Leaderboard also accessible at /api/leaderboard
from flask import Blueprint as _BP
