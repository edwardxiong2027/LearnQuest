"""Worksheet generation for printing."""

import os
import json
from flask import Blueprint, request, jsonify, current_app, Response

worksheets_bp = Blueprint('worksheets', __name__)


@worksheets_bp.route('/worksheet/<lesson_id>', methods=['GET'])
def get_worksheet(lesson_id):
    """Generate a printable HTML worksheet for a lesson."""
    subject = request.args.get('subject', 'math')
    grade = request.args.get('grade', '3')

    content_dir = current_app.config['CONTENT_DIR']
    grade_str = 'k' if grade == '0' else grade
    filepath = os.path.join(content_dir, subject, f'{grade_str}.json')

    if not os.path.exists(filepath):
        return jsonify({'error': 'Content not found'}), 404

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Find the lesson
    lesson = None
    for unit in data.get('units', []):
        for l in unit.get('lessons', []):
            if l.get('id') == lesson_id:
                lesson = l
                break
        if lesson:
            break

    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    problems = lesson.get('practice_problems', [])
    grade_label = 'Kindergarten' if grade == '0' else f'Grade {grade}'
    subject_names = {'math': 'Math', 'science': 'Science', 'ela': 'ELA', 'social_studies': 'Social Studies'}

    # Build printable HTML
    html = f'''<!DOCTYPE html>
<html><head>
<title>{lesson.get("title", "")} - Worksheet</title>
<style>
body {{ font-family: -apple-system, Arial, sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; color: #333; }}
h1 {{ font-size: 1.4rem; border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
.meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
.problem {{ margin: 1.5rem 0; padding: 0.75rem 0; border-bottom: 1px solid #ddd; }}
.problem-num {{ font-weight: bold; }}
.options {{ margin: 0.5rem 0 0 1.5rem; }}
.options div {{ margin: 0.25rem 0; }}
.answer-line {{ border-bottom: 1px solid #999; width: 200px; display: inline-block; margin-left: 0.5rem; }}
.answer-key {{ page-break-before: always; }}
.answer-key h2 {{ border-bottom: 2px solid #333; padding-bottom: 0.25rem; }}
.answer {{ margin: 0.5rem 0; }}
.name-line {{ border-bottom: 1px solid #333; width: 250px; display: inline-block; }}
@media print {{ body {{ margin: 1rem; }} }}
</style>
</head><body>

<h1>{_esc(lesson.get("title", ""))}</h1>
<div class="meta">{subject_names.get(subject, subject)} | {grade_label} | LearnQuest Worksheet</div>
<p>Name: <span class="name-line"></span> &nbsp; Date: <span class="name-line" style="width:150px"></span></p>

<hr>
'''

    for i, prob in enumerate(problems):
        html += f'<div class="problem"><span class="problem-num">{i+1}.</span> {_esc(prob.get("question", ""))}'

        if prob.get('type') == 'multiple_choice' and prob.get('options'):
            html += '<div class="options">'
            for j, opt in enumerate(prob['options']):
                letter = chr(65 + j)
                html += f'<div>{letter}. {_esc(str(opt))}</div>'
            html += '</div>'
        elif prob.get('type') == 'true_false':
            html += '<div class="options"><div>T. True</div><div>F. False</div></div>'
        else:
            html += f'<br>Answer: <span class="answer-line"></span>'

        html += '</div>'

    # Answer key on a new page
    html += '<div class="answer-key worksheet-answer-key"><h2>Answer Key</h2>'
    for i, prob in enumerate(problems):
        if prob.get('type') == 'multiple_choice' and prob.get('options'):
            correct_idx = prob.get('correct', 0)
            answer = prob['options'][correct_idx] if correct_idx < len(prob['options']) else '?'
            letter = chr(65 + correct_idx)
            html += f'<div class="answer"><strong>{i+1}.</strong> {letter}. {_esc(str(answer))}</div>'
        elif prob.get('type') == 'true_false':
            html += f'<div class="answer"><strong>{i+1}.</strong> {_esc(str(prob.get("answer", "")))}</div>'
        else:
            html += f'<div class="answer"><strong>{i+1}.</strong> {_esc(str(prob.get("answer", "")))}</div>'
    html += '</div></body></html>'

    return Response(html, mimetype='text/html')


def _esc(text):
    """Basic HTML escaping."""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
