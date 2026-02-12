"""Advanced algebra - quadratics, factoring, systems, polynomials, complex numbers (grades 9-12)."""

import random
import math
from fractions import Fraction
from sympy import symbols, solve, simplify, expand, factor, Eq, Rational, sqrt, I
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

x, y = symbols('x y')
TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def solve_quadratic(a, b, c):
    """Solve ax^2 + bx + c = 0. Returns list of solutions."""
    discriminant = b**2 - 4*a*c
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return sorted([round(x1, 4), round(x2, 4)])
    elif discriminant == 0:
        x1 = -b / (2*a)
        return [round(x1, 4)]
    else:
        real = -b / (2*a)
        imag = math.sqrt(-discriminant) / (2*a)
        return [f'{round(real, 4)} + {round(imag, 4)}i', f'{round(real, 4)} - {round(imag, 4)}i']


def factor_quadratic(a, b, c):
    """Factor ax^2 + bx + c using sympy."""
    expr = a * x**2 + b * x + c
    return str(factor(expr))


def solve_system_2x2(a1, b1, c1, a2, b2, c2):
    """Solve system: a1*x + b1*y = c1, a2*x + b2*y = c2."""
    solutions = solve([Eq(a1*x + b1*y, c1), Eq(a2*x + b2*y, c2)], [x, y])
    return solutions


def generate_quadratic_problems(grade, count=5):
    """Generate quadratic equation problems (factoring-friendly)."""
    problems = []
    for _ in range(count):
        r1 = random.randint(-6, 6)
        r2 = random.randint(-6, 6)
        a = 1
        b = -(r1 + r2)
        c = r1 * r2

        if b >= 0:
            b_str = f'+ {b}' if b > 0 else ''
        else:
            b_str = f'- {abs(b)}'
        if c >= 0:
            c_str = f'+ {c}' if c > 0 else ''
        else:
            c_str = f'- {abs(c)}'

        equation = f'x² {b_str}x {c_str} = 0'.replace('  ', ' ').strip()
        roots = sorted([r1, r2])
        answer = f'x = {roots[0]}, x = {roots[1]}' if r1 != r2 else f'x = {r1}'

        prob_type = random.choice(['solve', 'factor'])
        if prob_type == 'solve':
            problems.append({
                'type': 'fill_in',
                'question': f'Solve: {equation}',
                'answer': answer,
                'hint': 'Try factoring or use the quadratic formula: x = (-b ± √(b²-4ac)) / 2a'
            })
        else:
            factored = factor_quadratic(a, b, c)
            problems.append({
                'type': 'fill_in',
                'question': f'Factor: x² {b_str}x {c_str}'.strip(),
                'answer': factored,
                'hint': 'Find two numbers that multiply to give c and add to give b.'
            })
    return problems


def generate_system_problems(grade, count=5):
    """Generate systems of equations (2x2)."""
    problems = []
    for _ in range(count):
        sol_x = random.randint(-5, 5)
        sol_y = random.randint(-5, 5)

        a1 = random.choice([1, 2, 3, -1, -2])
        b1 = random.choice([1, 2, 3, -1, -2])
        c1 = a1 * sol_x + b1 * sol_y

        a2 = random.choice([1, 2, 3, -1, -2])
        b2 = random.choice([1, 2, 3, -1, -2])
        while a1 * b2 == a2 * b1:
            a2 = random.choice([1, 2, 3, -1, -2])
            b2 = random.choice([1, 2, 3, -1, -2])
        c2 = a2 * sol_x + b2 * sol_y

        def fmt_eq(a, b, c):
            parts = []
            if a == 1: parts.append('x')
            elif a == -1: parts.append('-x')
            else: parts.append(f'{a}x')
            if b == 1: parts.append('+ y')
            elif b == -1: parts.append('- y')
            elif b > 0: parts.append(f'+ {b}y')
            else: parts.append(f'- {abs(b)}y')
            return f'{" ".join(parts)} = {c}'

        eq1 = fmt_eq(a1, b1, c1)
        eq2 = fmt_eq(a2, b2, c2)

        problems.append({
            'type': 'fill_in',
            'question': f'Solve the system:\n{eq1}\n{eq2}',
            'answer': f'x = {sol_x}, y = {sol_y}',
            'hint': 'Try substitution or elimination to solve for one variable first.'
        })
    return problems


def generate_polynomial_problems(grade, count=5):
    """Generate polynomial operations problems."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['expand', 'simplify'])

        if prob_type == 'expand':
            a = random.randint(1, 3)
            b = random.randint(-5, 5)
            c = random.randint(1, 3)
            d = random.randint(-5, 5)
            expr = (a*x + b) * (c*x + d)
            expanded = expand(expr)
            problems.append({
                'type': 'fill_in',
                'question': f'Expand: ({a}x + {b})({c}x + {d})',
                'answer': str(expanded),
                'hint': 'Use FOIL: First, Outer, Inner, Last, then combine like terms.'
            })
        else:
            a = random.randint(1, 3)
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)
            d = random.randint(1, 3)
            e = random.randint(-5, 5)
            expr1 = a*x**2 + b*x + c
            expr2 = d*x + e
            result = simplify(expr1 + expr2)
            problems.append({
                'type': 'fill_in',
                'question': f'Simplify: ({a}x² + {b}x + {c}) + ({d}x + {e})',
                'answer': str(result),
                'hint': 'Combine like terms: group x² terms, x terms, and constants.'
            })
    return problems


def generate_complex_number_problems(grade, count=5):
    """Generate complex number arithmetic problems."""
    problems = []
    for _ in range(count):
        a1 = random.randint(-5, 5)
        b1 = random.randint(-5, 5)
        a2 = random.randint(-5, 5)
        b2 = random.randint(-5, 5)

        op = random.choice(['+', '-', '*'])
        z1 = a1 + b1*I
        z2 = a2 + b2*I

        if op == '+':
            result = simplify(z1 + z2)
            question = f'({a1} + {b1}i) + ({a2} + {b2}i)'
        elif op == '-':
            result = simplify(z1 - z2)
            question = f'({a1} + {b1}i) - ({a2} + {b2}i)'
        else:
            result = expand(z1 * z2)
            question = f'({a1} + {b1}i) * ({a2} + {b2}i)'

        answer = str(result).replace('*I', 'i').replace('I', 'i')

        problems.append({
            'type': 'fill_in',
            'question': f'Compute: {question}',
            'answer': answer,
            'hint': 'Remember that i² = -1. Combine real and imaginary parts separately.'
        })
    return problems
