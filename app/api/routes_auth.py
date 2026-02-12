"""Authentication routes - login, register, session management."""

from flask import Blueprint, request, jsonify, session, current_app

auth_bp = Blueprint('auth', __name__)


def get_db():
    return current_app.get_db()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name', '').strip()
    pin = data.get('pin', '')

    if not name or not pin:
        return jsonify({'error': 'Name and PIN are required'}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE name = ? AND pin = ?', (name, pin)
    ).fetchone()

    if not user:
        return jsonify({'error': 'Invalid name or PIN'}), 401

    # Update streak
    import datetime
    today = datetime.date.today().isoformat()
    last_active = user['last_active']
    streak = user['streak_days']

    if last_active:
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        if last_active == yesterday:
            streak += 1
        elif last_active != today:
            streak = 1
    else:
        streak = 1

    db.execute(
        'UPDATE users SET last_active = ?, streak_days = ? WHERE id = ?',
        (today, streak, user['id'])
    )
    db.commit()

    session['user_id'] = user['id']

    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'role': user['role'],
            'grade': user['grade'],
            'avatar': user['avatar'],
            'xp': user['xp'],
            'level': user['level'],
            'streak_days': streak,
        }
    })


@auth_bp.route('/register', methods=['POST'])
def register():
    # Only teachers can register students
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    teacher = db.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not teacher or teacher['role'] != 'teacher':
        return jsonify({'error': 'Only teachers can register students'}), 403

    data = request.get_json()
    name = data.get('name', '').strip()
    pin = data.get('pin', '')
    grade = data.get('grade', 3)

    if not name or not pin:
        return jsonify({'error': 'Name and PIN are required'}), 400

    # Check if name already exists
    existing = db.execute('SELECT id FROM users WHERE name = ?', (name,)).fetchone()
    if existing:
        return jsonify({'error': 'A user with that name already exists'}), 400

    db.execute(
        'INSERT INTO users (name, pin, role, grade) VALUES (?, ?, ?, ?)',
        (name, pin, 'student', grade)
    )
    db.commit()

    return jsonify({'message': 'Student created successfully'})


@auth_bp.route('/session', methods=['GET'])
def get_session():
    if 'user_id' not in session:
        return jsonify({'user': None})

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if not user:
        session.pop('user_id', None)
        return jsonify({'user': None})

    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'role': user['role'],
            'grade': user['grade'],
            'avatar': user['avatar'],
            'xp': user['xp'],
            'level': user['level'],
            'streak_days': user['streak_days'],
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})
