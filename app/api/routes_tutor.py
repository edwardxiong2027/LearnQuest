"""AI Tutor routes - chat, hints, conversation management via Ollama/Phi-3."""

import json
import hashlib
import datetime
from flask import Blueprint, request, jsonify, session, current_app, Response, stream_with_context
from api.llm_utils import load_prompt, call_ollama, get_cached_response, cache_response

tutor_bp = Blueprint('tutor', __name__)


def get_db():
    return current_app.get_db()


@tutor_bp.route('/chat', methods=['POST'])
def chat():
    """Send a message to the AI tutor."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')
    lesson_id = data.get('lesson_id')
    subject = data.get('subject', 'math')
    grade = data.get('grade', 3)

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    db = get_db()
    user_id = session['user_id']

    # Auto-create conversation if it doesn't exist
    existing_conv = db.execute(
        'SELECT id FROM conversations WHERE user_id = ? AND session_id = ?',
        (user_id, session_id)
    ).fetchone()
    if not existing_conv:
        # Use first message as initial title (truncated)
        title = message[:50] + ('...' if len(message) > 50 else '')
        db.execute(
            'INSERT INTO conversations (user_id, session_id, title, subject) VALUES (?, ?, ?, ?)',
            (user_id, session_id, title, subject)
        )
        db.commit()

    # Save user message
    db.execute(
        'INSERT INTO chat_history (user_id, session_id, lesson_id, role, message) VALUES (?, ?, ?, ?, ?)',
        (user_id, session_id, lesson_id, 'user', message)
    )
    db.commit()

    # Update conversation timestamp
    db.execute(
        'UPDATE conversations SET updated_at = ? WHERE user_id = ? AND session_id = ?',
        (datetime.datetime.now().isoformat(), user_id, session_id)
    )
    db.commit()

    # Award tutor badge on first use
    from api.routes_quiz import _award_badge
    _award_badge(db, user_id, 'tutor_user', 'Help Seeker', 'Use the AI tutor')
    db.commit()

    # Build prompt
    prompt_map = {
        'math': 'tutor_math.txt',
        'science': 'tutor_science.txt',
        'ela': 'tutor_ela.txt',
        'social_studies': 'tutor_social.txt'
    }
    system_prompt = load_prompt(
        prompt_map.get(subject, 'tutor_math.txt'),
        grade=grade,
        topic=subject,
        lesson_title=lesson_id or 'General'
    )

    # Get recent chat history
    history = db.execute(
        'SELECT role, message FROM chat_history WHERE user_id = ? AND session_id = ? ORDER BY created_at DESC LIMIT 10',
        (user_id, session_id)
    ).fetchall()
    history = list(reversed(history))

    messages = [{'role': 'system', 'content': system_prompt}]
    for h in history:
        role = 'user' if h['role'] == 'user' else 'assistant'
        messages.append({'role': role, 'content': h['message']})

    # Check cache
    cache_key = hashlib.md5(json.dumps(messages[-3:], sort_keys=True).encode()).hexdigest()
    cached = get_cached_response(db, cache_key)
    if cached:
        db.execute(
            'INSERT INTO chat_history (user_id, session_id, lesson_id, role, message) VALUES (?, ?, ?, ?, ?)',
            (user_id, session_id, lesson_id, 'assistant', cached)
        )
        db.commit()
        return jsonify({'response': cached})

    # Try streaming response
    try:
        resp = call_ollama(messages, stream=True)
        if hasattr(resp, 'iter_lines'):
            def generate():
                full_response = ''
                for line in resp.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get('message', {}).get('content', '')
                            if token:
                                full_response += token
                                yield f"data: {json.dumps({'token': token})}\n\n"
                            if data.get('done'):
                                yield "data: [DONE]\n\n"
                                try:
                                    db2 = get_db()
                                    db2.execute(
                                        'INSERT INTO chat_history (user_id, session_id, lesson_id, role, message) VALUES (?, ?, ?, ?, ?)',
                                        (user_id, session_id, lesson_id, 'assistant', full_response)
                                    )
                                    db2.commit()
                                    cache_response(db2, cache_key, full_response)
                                except:
                                    pass
                                break
                        except json.JSONDecodeError:
                            continue

            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
    except:
        pass

    # Fallback: non-streaming
    response = call_ollama(messages, stream=False)

    db.execute(
        'INSERT INTO chat_history (user_id, session_id, lesson_id, role, message) VALUES (?, ?, ?, ?, ?)',
        (user_id, session_id, lesson_id, 'assistant', response)
    )
    db.commit()
    cache_response(db, cache_key, response)

    return jsonify({'response': response})


@tutor_bp.route('/hint', methods=['POST'])
def get_hint():
    """Get a hint for a specific problem."""
    data = request.get_json()
    problem = data.get('problem', '')
    subject = data.get('subject', 'math')
    grade = data.get('grade', 3)

    if not problem:
        return jsonify({'hint': 'Try breaking the problem into smaller steps!'})

    db = get_db()
    system_prompt = load_prompt('hint_generator.txt', grade=grade, subject=subject)
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Give me a hint for this problem: {problem}"}
    ]

    cache_key = hashlib.md5(f"hint:{problem}:{grade}".encode()).hexdigest()
    cached = get_cached_response(db, cache_key)
    if cached:
        return jsonify({'hint': cached})

    response = call_ollama(messages, stream=False)
    cache_response(db, cache_key, response)

    return jsonify({'hint': response})


# ---------------------------------------------------------------------------
# Conversation management endpoints
# ---------------------------------------------------------------------------

@tutor_bp.route('/conversations', methods=['GET'])
def list_conversations():
    """List all conversations for the current user."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']

    rows = db.execute(
        '''SELECT c.id, c.session_id, c.title, c.subject, c.pinned, c.created_at, c.updated_at,
                  (SELECT COUNT(*) FROM chat_history ch WHERE ch.user_id = c.user_id AND ch.session_id = c.session_id) as message_count
           FROM conversations c
           WHERE c.user_id = ?
           ORDER BY c.pinned DESC, c.updated_at DESC''',
        (user_id,)
    ).fetchall()

    return jsonify({'conversations': [dict(r) for r in rows]})


@tutor_bp.route('/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    subject = data.get('subject', 'math')
    session_id = f"session_{int(datetime.datetime.now().timestamp() * 1000)}"

    db = get_db()
    user_id = session['user_id']

    db.execute(
        'INSERT INTO conversations (user_id, session_id, title, subject) VALUES (?, ?, ?, ?)',
        (user_id, session_id, 'New Conversation', subject)
    )
    db.commit()

    conv = db.execute(
        'SELECT * FROM conversations WHERE user_id = ? AND session_id = ?',
        (user_id, session_id)
    ).fetchone()

    return jsonify({'conversation': dict(conv)})


@tutor_bp.route('/conversations/<int:conv_id>', methods=['PUT'])
def update_conversation(conv_id):
    """Rename a conversation."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    db = get_db()
    db.execute(
        'UPDATE conversations SET title = ? WHERE id = ? AND user_id = ?',
        (title, conv_id, session['user_id'])
    )
    db.commit()
    return jsonify({'message': 'Updated'})


@tutor_bp.route('/conversations/<int:conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    """Delete a conversation and its messages."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']

    # Get session_id first
    conv = db.execute('SELECT session_id FROM conversations WHERE id = ? AND user_id = ?', (conv_id, user_id)).fetchone()
    if conv:
        db.execute('DELETE FROM chat_history WHERE user_id = ? AND session_id = ?', (user_id, conv['session_id']))
        db.execute('DELETE FROM conversations WHERE id = ? AND user_id = ?', (conv_id, user_id))
        db.commit()

    return jsonify({'message': 'Deleted'})


@tutor_bp.route('/conversations/<int:conv_id>/pin', methods=['POST'])
def toggle_pin_conversation(conv_id):
    """Toggle pin status on a conversation."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']

    conv = db.execute('SELECT pinned FROM conversations WHERE id = ? AND user_id = ?', (conv_id, user_id)).fetchone()
    if not conv:
        return jsonify({'error': 'Not found'}), 404

    new_pinned = 0 if conv['pinned'] else 1
    db.execute('UPDATE conversations SET pinned = ? WHERE id = ? AND user_id = ?', (new_pinned, conv_id, user_id))
    db.commit()
    return jsonify({'pinned': bool(new_pinned)})


@tutor_bp.route('/conversations/<int:conv_id>/messages', methods=['GET'])
def get_conversation_messages(conv_id):
    """Get all messages for a conversation."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    user_id = session['user_id']

    conv = db.execute('SELECT session_id, subject FROM conversations WHERE id = ? AND user_id = ?', (conv_id, user_id)).fetchone()
    if not conv:
        return jsonify({'error': 'Not found'}), 404

    messages = db.execute(
        'SELECT role, message, created_at FROM chat_history WHERE user_id = ? AND session_id = ? ORDER BY created_at ASC',
        (user_id, conv['session_id'])
    ).fetchall()

    return jsonify({
        'messages': [dict(m) for m in messages],
        'session_id': conv['session_id'],
        'subject': conv['subject']
    })
