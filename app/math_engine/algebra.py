"""Algebra operations - expressions, equations, simplification (grades 6-12)."""

import random
from sympy import symbols, solve, simplify, Eq, parse_expr, Rational
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application


x = symbols('x')

TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def solve_linear_equation(equation_str):
    """Solve a linear equation. Returns the value of x."""
    try:
        # Parse "2x + 3 = 7" format
        if '=' in equation_str:
            left, right = equation_str.split('=')
            left_expr = parse_expr(left.strip(), transformations=TRANSFORMS)
            right_expr = parse_expr(right.strip(), transformations=TRANSFORMS)
            eq = Eq(left_expr, right_expr)
        else:
            eq = Eq(parse_expr(equation_str, transformations=TRANSFORMS), 0)

        solutions = solve(eq, x)
        return solutions
    except Exception as e:
        raise ValueError(f"Cannot solve equation: {e}")


def evaluate_expression(expr_str, x_value=None):
    """Evaluate a mathematical expression, optionally substituting x."""
    try:
        expr = parse_expr(expr_str, transformations=TRANSFORMS)
        if x_value is not None:
            expr = expr.subs(x, Rational(x_value))
        return simplify(expr)
    except Exception as e:
        raise ValueError(f"Cannot evaluate: {e}")


def generate_linear_equations(grade, count=5):
    """Generate linear equation problems."""
    problems = []
    for _ in range(count):
        if grade == 6:
            # Simple: ax + b = c
            a = random.choice([1, 2, 3, 4, 5])
            answer = random.randint(-10, 10)
            b = random.randint(-10, 10)
            c = a * answer + b
            equation = f'{a}x + {b} = {c}' if b >= 0 else f'{a}x - {abs(b)} = {c}'
            if a == 1:
                equation = equation.replace('1x', 'x')
        elif grade == 7:
            # ax + b = cx + d
            a = random.randint(2, 6)
            c_val = random.randint(1, a - 1)
            answer = random.randint(-5, 10)
            b = random.randint(-10, 10)
            d = a * answer + b - c_val * answer
            equation = f'{a}x + {b} = {c_val}x + {d}'
        elif grade == 8:
            # More complex
            a = random.randint(2, 8)
            b = random.randint(-15, 15)
            answer = random.randint(-10, 10)
            c = a * answer + b
            equation = f'{a}x + {b} = {c}' if b >= 0 else f'{a}x - {abs(b)} = {c}'
        else:
            # Grades 9+: multi-step with fractions
            a = random.randint(2, 6)
            b = random.randint(-8, 8)
            c_coeff = random.randint(1, 4)
            answer = random.randint(-5, 10)
            d = a * answer + b - c_coeff * answer
            equation = f'{a}x + {b} = {c_coeff}x + {d}'

        problems.append({
            'type': 'fill_in',
            'question': f'Solve for x: {equation}',
            'answer': str(answer),
            'hint': 'Isolate x by doing the same operation on both sides of the equation.'
        })
    return problems


def generate_expression_evaluation(grade, count=5):
    """Generate expression evaluation problems."""
    problems = []
    for _ in range(count):
        x_val = random.randint(1, 10)

        if grade <= 6:
            a = random.randint(1, 5)
            b = random.randint(1, 10)
            expr = f'{a}x + {b}'
            answer = a * x_val + b
        else:
            a = random.randint(1, 5)
            b = random.randint(-5, 5)
            c = random.randint(-10, 10)
            expr = f'{a}x² + {b}x + {c}' if grade == 8 else f'{a}x + {b}'
            if grade == 8:
                answer = a * x_val**2 + b * x_val + c
            else:
                answer = a * x_val + b

        problems.append({
            'type': 'fill_in',
            'question': f'If x = {x_val}, what is {expr}?',
            'answer': str(answer),
            'hint': f'Replace x with {x_val} and calculate step by step.'
        })
    return problems
