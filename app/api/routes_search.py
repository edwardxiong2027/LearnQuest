"""Search across all curriculum content."""

import os
import json
from flask import Blueprint, request, jsonify, current_app

search_bp = Blueprint('search', __name__)

# In-memory search index, built on first call
_search_index = None


def _build_index():
    """Build search index from all curriculum JSON files."""
    global _search_index
    content_dir = current_app.config['CONTENT_DIR']
    index = []

    for subject in ['math', 'science', 'ela', 'social_studies']:
        subject_dir = os.path.join(content_dir, subject)
        if not os.path.isdir(subject_dir):
            continue

        for filename in os.listdir(subject_dir):
            if not filename.endswith('.json'):
                continue

            grade_str = filename.replace('.json', '')
            grade = 0 if grade_str == 'k' else int(grade_str) if grade_str.isdigit() else None
            if grade is None:
                continue

            filepath = os.path.join(subject_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            for unit in data.get('units', []):
                for lesson in unit.get('lessons', []):
                    content = lesson.get('content', {})
                    searchable = ' '.join([
                        lesson.get('title', ''),
                        unit.get('title', ''),
                        content.get('explanation', ''),
                        ' '.join(content.get('key_vocabulary', [])),
                        content.get('real_world', '')
                    ]).lower()

                    index.append({
                        'lesson_id': lesson.get('id', ''),
                        'title': lesson.get('title', ''),
                        'unit_title': unit.get('title', ''),
                        'subject': subject,
                        'grade': grade,
                        'searchable': searchable
                    })

    _search_index = index
    return index


@search_bp.route('/search', methods=['GET'])
def search():
    """Search across all curriculum content."""
    query = request.args.get('q', '').strip().lower()
    if len(query) < 2:
        return jsonify({'results': []})

    global _search_index
    if _search_index is None:
        _build_index()

    results = []
    terms = query.split()

    for item in _search_index:
        # All terms must appear in searchable text
        if all(term in item['searchable'] for term in terms):
            # Build context snippet
            text = item['searchable']
            pos = text.find(terms[0])
            start = max(0, pos - 30)
            end = min(len(text), pos + 60)
            context = text[start:end].strip()
            if start > 0:
                context = '...' + context
            if end < len(text):
                context = context + '...'

            results.append({
                'lesson_id': item['lesson_id'],
                'title': item['title'],
                'unit_title': item['unit_title'],
                'subject': item['subject'],
                'grade': item['grade'],
                'context': context
            })

    # Sort: exact title matches first
    results.sort(key=lambda r: (0 if query in r['title'].lower() else 1))

    return jsonify({'results': results[:20]})
