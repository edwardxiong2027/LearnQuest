"""Pre-calculus operations - logarithms, exponentials, limits, matrices, vectors (grades 11-12)."""

import random
import math
from fractions import Fraction
from sympy import (symbols, log, exp, limit, oo, simplify, Matrix, Rational,
                   ln, solve, sqrt, pi)

x = symbols('x')


def evaluate_log(base, argument):
    """Evaluate log_base(argument)."""
    if argument <= 0 or base <= 0 or base == 1:
        return None
    return round(math.log(argument) / math.log(base), 6)


def evaluate_natural_log(argument):
    """Evaluate ln(argument)."""
    if argument <= 0:
        return None
    return round(math.log(argument), 6)


def compute_limit(expr_str, var='x', point='oo'):
    """Compute limit of expression as var approaches point."""
    try:
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        transforms = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, transformations=transforms)
        x_sym = symbols(var)
        if point == 'oo':
            result = limit(expr, x_sym, oo)
        elif point == '-oo':
            result = limit(expr, x_sym, -oo)
        else:
            result = limit(expr, x_sym, float(point))
        return str(result)
    except Exception:
        return None


def matrix_multiply_2x2(a, b):
    """Multiply two 2x2 matrices."""
    A = Matrix(a)
    B = Matrix(b)
    return (A * B).tolist()


def matrix_determinant_2x2(a, b, c, d):
    """Compute determinant of [[a,b],[c,d]]."""
    return a * d - b * c


def dot_product(v1, v2):
    """Compute dot product of two vectors."""
    return sum(a * b for a, b in zip(v1, v2))


def vector_magnitude(v):
    """Compute magnitude of a vector."""
    return round(math.sqrt(sum(c**2 for c in v)), 4)


def generate_logarithm_problems(grade, count=5):
    """Generate logarithm problems."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['evaluate', 'property', 'solve'])

        if prob_type == 'evaluate':
            base = random.choice([2, 3, 5, 10])
            exp_val = random.randint(1, 4)
            argument = base ** exp_val
            problems.append({
                'type': 'fill_in',
                'question': f'Evaluate: log_{base}({argument})',
                'answer': str(exp_val),
                'hint': f'Ask yourself: {base} raised to what power equals {argument}?'
            })
        elif prob_type == 'property':
            base = random.choice([2, 10])
            a = base ** random.randint(1, 3)
            b = base ** random.randint(1, 3)
            product = a * b
            answer = round(math.log(product) / math.log(base))
            problems.append({
                'type': 'fill_in',
                'question': f'Simplify: log_{base}({a}) + log_{base}({b})',
                'answer': str(int(answer)),
                'hint': 'Use the product rule: log(a) + log(b) = log(a*b)'
            })
        else:
            base = random.choice([2, 3])
            result = random.randint(2, 5)
            answer = base ** result
            problems.append({
                'type': 'fill_in',
                'question': f'Solve for x: log_{base}(x) = {result}',
                'answer': str(answer),
                'hint': f'Rewrite in exponential form: {base}^{result} = x'
            })
    return problems


def generate_exponential_problems(grade, count=5):
    """Generate exponential growth/decay problems."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['evaluate', 'growth'])

        if prob_type == 'evaluate':
            base = random.choice([2, 3, 5])
            exp_val = random.randint(-2, 4)
            answer = base ** exp_val
            if exp_val < 0:
                answer = Fraction(1, base ** abs(exp_val))
                answer_str = str(answer)
            else:
                answer_str = str(answer)
            problems.append({
                'type': 'fill_in',
                'question': f'Evaluate: {base}^{exp_val}',
                'answer': answer_str,
                'hint': 'For negative exponents, take the reciprocal.'
            })
        else:
            initial = random.choice([100, 200, 500, 1000])
            rate = random.choice([2, 3, 5, 10]) / 100
            years = random.randint(1, 3)
            answer = round(initial * (1 + rate) ** years, 2)
            problems.append({
                'type': 'fill_in',
                'question': f'An investment of ${initial} grows at {int(rate*100)}% per year. What is its value after {years} year(s)?',
                'answer': str(answer),
                'hint': 'Use the formula A = P(1 + r)^t'
            })
    return problems


def generate_limit_problems(grade, count=5):
    """Generate basic limit problems."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['polynomial', 'rational', 'infinity'])

        if prob_type == 'polynomial':
            a = random.randint(1, 3)
            b = random.randint(-5, 5)
            c_val = random.randint(-3, 3)
            answer = a * c_val**2 + b * c_val
            problems.append({
                'type': 'fill_in',
                'question': f'Find: lim(x→{c_val}) ({a}x² + {b}x)',
                'answer': str(answer),
                'hint': 'For polynomial limits, just substitute the value of x.'
            })
        elif prob_type == 'rational':
            r = random.randint(1, 5)
            problems.append({
                'type': 'fill_in',
                'question': f'Find: lim(x→{r}) (x² - {r**2})/(x - {r})',
                'answer': str(2 * r),
                'hint': 'Factor the numerator as a difference of squares, then cancel.'
            })
        else:
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            answer_frac = Fraction(a, b)
            problems.append({
                'type': 'fill_in',
                'question': f'Find: lim(x→∞) ({a}x + 3)/({b}x - 1)',
                'answer': str(answer_frac),
                'hint': 'Divide numerator and denominator by the highest power of x.'
            })
    return problems


def generate_matrix_problems(grade, count=5):
    """Generate matrix operation problems."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['determinant', 'add', 'multiply'])

        if prob_type == 'determinant':
            a, b, c, d = [random.randint(-5, 5) for _ in range(4)]
            det = a * d - b * c
            problems.append({
                'type': 'fill_in',
                'question': f'Find the determinant of the matrix [[{a}, {b}], [{c}, {d}]]',
                'answer': str(det),
                'hint': 'For a 2x2 matrix [[a,b],[c,d]], det = ad - bc'
            })
        elif prob_type == 'add':
            a1, b1, c1, d1 = [random.randint(-5, 5) for _ in range(4)]
            a2, b2, c2, d2 = [random.randint(-5, 5) for _ in range(4)]
            result = [[a1+a2, b1+b2], [c1+c2, d1+d2]]
            problems.append({
                'type': 'fill_in',
                'question': f'Add: [[{a1},{b1}],[{c1},{d1}]] + [[{a2},{b2}],[{c2},{d2}]]',
                'answer': str(result),
                'hint': 'Add corresponding elements.'
            })
        else:
            vals = [random.randint(-3, 3) for _ in range(4)]
            det = vals[0]*vals[3] - vals[1]*vals[2]
            problems.append({
                'type': 'fill_in',
                'question': f'Find the determinant: |{vals[0]} {vals[1]}| / |{vals[2]} {vals[3]}|',
                'answer': str(det),
                'hint': 'det = ad - bc for a 2x2 matrix.'
            })
    return problems


def generate_vector_problems(grade, count=5):
    """Generate vector operation problems."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['magnitude', 'dot_product', 'add'])

        if prob_type == 'magnitude':
            a = random.randint(1, 8)
            b = random.randint(1, 8)
            mag = round(math.sqrt(a**2 + b**2), 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the magnitude of vector <{a}, {b}>',
                'answer': str(mag),
                'hint': 'Magnitude = √(a² + b²)'
            })
        elif prob_type == 'dot_product':
            a1, a2 = random.randint(-5, 5), random.randint(-5, 5)
            b1, b2 = random.randint(-5, 5), random.randint(-5, 5)
            result = a1*b1 + a2*b2
            problems.append({
                'type': 'fill_in',
                'question': f'Find the dot product: <{a1}, {a2}> · <{b1}, {b2}>',
                'answer': str(result),
                'hint': 'Dot product = a1*b1 + a2*b2'
            })
        else:
            a1, a2 = random.randint(-5, 5), random.randint(-5, 5)
            b1, b2 = random.randint(-5, 5), random.randint(-5, 5)
            problems.append({
                'type': 'fill_in',
                'question': f'Add vectors: <{a1}, {a2}> + <{b1}, {b2}>',
                'answer': f'<{a1+b1}, {a2+b2}>',
                'hint': 'Add corresponding components.'
            })
    return problems
