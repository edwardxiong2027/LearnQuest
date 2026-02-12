"""Arithmetic operations - addition, subtraction, multiplication, division."""

import random
from fractions import Fraction


def compute(expression):
    """Safely evaluate an arithmetic expression and return the result."""
    # Clean the expression
    expr = expression.strip()
    expr = expr.replace('×', '*').replace('÷', '/').replace('−', '-')

    # Use Fraction for exact arithmetic
    try:
        # Parse and evaluate safely
        result = _safe_eval(expr)
        return result
    except Exception:
        return None


def _safe_eval(expr):
    """Safely evaluate a simple arithmetic expression using Fraction."""
    # Only allow: digits, +, -, *, /, (, ), ., spaces
    allowed = set('0123456789+-*/().  ')
    if not all(c in allowed for c in expr):
        raise ValueError(f"Invalid character in expression: {expr}")

    # Replace integer/decimal literals with Fraction
    import re
    # Convert to use Fraction for precision
    tokens = re.split(r'(\d+\.?\d*)', expr)
    frac_expr = ''
    for token in tokens:
        if re.match(r'^\d+\.?\d*$', token):
            frac_expr += f'Fraction("{token}")'
        else:
            frac_expr += token

    result = eval(frac_expr, {"__builtins__": {}, "Fraction": Fraction})
    return result


def generate_addition(grade, count=5):
    """Generate addition problems appropriate for grade level."""
    problems = []
    for _ in range(count):
        if grade <= 1:
            a, b = random.randint(0, 10), random.randint(0, 10)
        elif grade == 2:
            a, b = random.randint(0, 50), random.randint(0, 50)
        elif grade <= 4:
            a, b = random.randint(10, 500), random.randint(10, 500)
        else:
            a, b = random.randint(100, 9999), random.randint(100, 9999)

        answer = a + b
        problems.append({
            'type': 'fill_in',
            'question': f'What is {a} + {b}?',
            'answer': str(answer),
            'operation': f'{a} + {b}',
            'hint': f'Start by adding the ones place: {a % 10} + {b % 10}'
        })
    return problems


def generate_subtraction(grade, count=5):
    """Generate subtraction problems appropriate for grade level."""
    problems = []
    for _ in range(count):
        if grade <= 1:
            a = random.randint(1, 10)
            b = random.randint(0, a)
        elif grade == 2:
            a = random.randint(10, 100)
            b = random.randint(0, a)
        elif grade <= 4:
            a = random.randint(50, 1000)
            b = random.randint(1, a)
        else:
            a = random.randint(100, 9999)
            b = random.randint(1, a)

        answer = a - b
        problems.append({
            'type': 'fill_in',
            'question': f'What is {a} - {b}?',
            'answer': str(answer),
            'operation': f'{a} - {b}',
            'hint': f'Think: what plus {b} equals {a}?'
        })
    return problems


def generate_multiplication(grade, count=5):
    """Generate multiplication problems appropriate for grade level."""
    problems = []
    for _ in range(count):
        if grade <= 3:
            a, b = random.randint(1, 10), random.randint(1, 10)
        elif grade == 4:
            a = random.randint(10, 99)
            b = random.randint(2, 12)
        else:
            a = random.randint(10, 999)
            b = random.randint(2, 99)

        answer = a * b
        problems.append({
            'type': 'fill_in',
            'question': f'What is {a} × {b}?',
            'answer': str(answer),
            'operation': f'{a} * {b}',
            'hint': f'Think of {a} groups of {b}'
        })
    return problems


def generate_division(grade, count=5):
    """Generate division problems with whole-number answers."""
    problems = []
    for _ in range(count):
        if grade <= 3:
            b = random.randint(1, 10)
            answer = random.randint(1, 10)
        elif grade == 4:
            b = random.randint(2, 12)
            answer = random.randint(2, 25)
        else:
            b = random.randint(2, 20)
            answer = random.randint(2, 50)

        a = b * answer  # Ensure clean division
        problems.append({
            'type': 'fill_in',
            'question': f'What is {a} ÷ {b}?',
            'answer': str(answer),
            'operation': f'{a} / {b}',
            'hint': f'Think: {b} times what equals {a}?'
        })
    return problems
