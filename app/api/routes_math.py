"""Math engine API routes - answer checking, step-by-step solving."""

from flask import Blueprint, request, jsonify
from math_engine.answer_validator import validate_answer
from math_engine.step_solver import solve_steps
from math_engine.problem_generator import generate_problems

math_bp = Blueprint('math', __name__)


@math_bp.route('/check', methods=['POST'])
def check_answer():
    """Validate a student's math answer against the correct answer."""
    data = request.get_json()
    student_answer = data.get('student_answer', '')
    correct_answer = data.get('correct_answer', '')

    if not student_answer or not correct_answer:
        return jsonify({'error': 'Both student_answer and correct_answer required'}), 400

    is_correct = validate_answer(student_answer, correct_answer)

    return jsonify({
        'correct': is_correct,
        'student_answer': student_answer,
        'correct_answer': correct_answer
    })


@math_bp.route('/solve', methods=['POST'])
def solve():
    """Get step-by-step solution for a math problem."""
    data = request.get_json()
    problem = data.get('problem', '')
    problem_type = data.get('type', '') or data.get('topic', '')
    grade = data.get('grade', 3)

    # Auto-detect problem type if not specified
    if not problem_type:
        if '/' in problem and any(c in problem for c in '+-×÷*'):
            problem_type = 'fractions'
        elif '=' in problem or 'x' in problem.lower():
            problem_type = 'equation'
        elif any(w in problem.lower() for w in ('area', 'perimeter', 'volume')):
            problem_type = 'geometry'
        else:
            problem_type = 'arithmetic'

    if not problem:
        return jsonify({'error': 'Problem is required'}), 400

    try:
        steps = solve_steps(problem, problem_type)
        return jsonify({
            'problem': problem,
            'steps': steps['steps'],
            'answer': steps['answer']
        })
    except Exception as e:
        return jsonify({'error': f'Could not solve: {str(e)}'}), 400


@math_bp.route('/generate', methods=['POST'])
def generate():
    """Generate practice problems for a given topic and grade."""
    data = request.get_json()
    topic = data.get('topic', 'addition')
    grade = data.get('grade', 3)
    count = min(data.get('count', 5), 20)

    try:
        problems = generate_problems(topic, grade, count)
        return jsonify({'problems': problems})
    except Exception as e:
        return jsonify({'error': f'Could not generate: {str(e)}'}), 400
