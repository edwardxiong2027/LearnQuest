"""Step-by-step math solver - generates deterministic solution steps."""

from fractions import Fraction
import re


def solve_steps(problem, problem_type='arithmetic'):
    """Generate step-by-step solution for a math problem."""
    problem = problem.strip()

    if problem_type in ('arithmetic', 'addition', 'subtraction', 'multiplication', 'division'):
        return _solve_arithmetic(problem)
    elif problem_type in ('fraction', 'fractions'):
        return _solve_fraction(problem)
    elif problem_type in ('equation', 'linear', 'algebra'):
        return _solve_equation(problem)
    elif problem_type in ('area', 'perimeter', 'geometry'):
        return _solve_geometry(problem)
    elif problem_type in ('quadratic',):
        return _solve_quadratic(problem)
    elif problem_type in ('trig', 'trigonometry'):
        return _solve_trig(problem)
    elif problem_type in ('logarithm', 'log'):
        return _solve_logarithm(problem)
    else:
        return _solve_arithmetic(problem)


def _solve_arithmetic(problem):
    """Solve basic arithmetic step by step."""
    # Clean up
    expr = problem.replace('×', '*').replace('÷', '/').replace('−', '-')
    expr = re.sub(r'[Ww]hat is\s*', '', expr)
    expr = expr.replace('?', '').strip()

    try:
        result = eval(expr, {"__builtins__": {}})
    except:
        return {'steps': ['Could not parse the expression.'], 'answer': 'Unknown'}

    steps = [
        f"Start with: {problem}",
        f"Calculate: {expr}",
        f"The answer is: {result}"
    ]

    return {'steps': steps, 'answer': str(result)}


def _solve_fraction(problem):
    """Solve fraction problems step by step."""
    # Try to extract fractions and operator
    frac_pattern = r'(\d+)\s*/\s*(\d+)'
    fractions = re.findall(frac_pattern, problem)

    if len(fractions) < 2:
        return _solve_arithmetic(problem)

    a = Fraction(int(fractions[0][0]), int(fractions[0][1]))
    b = Fraction(int(fractions[1][0]), int(fractions[1][1]))

    if '+' in problem:
        op = '+'
        result = a + b
    elif '-' in problem or '−' in problem:
        op = '-'
        result = a - b
    elif '×' in problem or '*' in problem:
        op = '×'
        result = a * b
    elif '÷' in problem or '/' in problem.replace(f'{fractions[0][0]}/{fractions[0][1]}', '').replace(f'{fractions[1][0]}/{fractions[1][1]}', ''):
        op = '÷'
        result = a / b
    else:
        op = '+'
        result = a + b

    steps = [f"Start with: {a} {op} {b}"]

    if op in ('+', '-'):
        if a.denominator != b.denominator:
            from math import gcd
            lcd = a.denominator * b.denominator // gcd(a.denominator, b.denominator)
            new_a_num = a.numerator * (lcd // a.denominator)
            new_b_num = b.numerator * (lcd // b.denominator)
            steps.append(f"Find common denominator: {lcd}")
            steps.append(f"Convert: {new_a_num}/{lcd} {op} {new_b_num}/{lcd}")
        else:
            steps.append(f"Same denominator: {a.denominator}")

    elif op == '×':
        steps.append(f"Multiply numerators: {a.numerator} × {b.numerator} = {a.numerator * b.numerator}")
        steps.append(f"Multiply denominators: {a.denominator} × {b.denominator} = {a.denominator * b.denominator}")

    elif op == '÷':
        steps.append(f"Flip the second fraction: {b.denominator}/{b.numerator}")
        steps.append(f"Then multiply: {a} × {b.denominator}/{b.numerator}")

    # Simplify if needed
    if result.denominator == 1:
        answer_str = str(result.numerator)
    elif abs(result.numerator) > result.denominator:
        whole = result.numerator // result.denominator
        rem = abs(result.numerator) % result.denominator
        if rem == 0:
            answer_str = str(whole)
        else:
            answer_str = f"{whole} {rem}/{result.denominator}"
            steps.append(f"Convert to mixed number: {answer_str}")
    else:
        answer_str = f"{result.numerator}/{result.denominator}"

    steps.append(f"Answer: {answer_str}")

    return {'steps': steps, 'answer': answer_str}


def _solve_equation(problem):
    """Solve a linear equation step by step."""
    # Extract equation
    eq = problem.replace('Solve for x:', '').replace('Solve:', '').strip()

    try:
        from sympy import symbols, solve, Eq
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        x = symbols('x')
        transforms = standard_transformations + (implicit_multiplication_application,)

        if '=' in eq:
            left, right = eq.split('=')
            left_expr = parse_expr(left.strip(), transformations=transforms)
            right_expr = parse_expr(right.strip(), transformations=transforms)
            solution = solve(Eq(left_expr, right_expr), x)
        else:
            solution = solve(parse_expr(eq, transformations=transforms), x)

        answer = str(solution[0]) if solution else 'No solution'

        steps = [
            f"Start with: {eq}",
            f"Isolate x on one side",
            f"x = {answer}"
        ]

        return {'steps': steps, 'answer': answer}
    except Exception as e:
        return {'steps': [f'Could not solve: {e}'], 'answer': 'Unknown'}


def _solve_geometry(problem):
    """Solve geometry problems step by step."""
    # Simple pattern matching for common geometry problems
    problem_lower = problem.lower()

    if 'area' in problem_lower and 'rectangle' in problem_lower:
        nums = [int(n) for n in re.findall(r'\d+', problem)]
        if len(nums) >= 2:
            area = nums[0] * nums[1]
            return {
                'steps': [
                    f'Area of a rectangle = length × width',
                    f'= {nums[0]} × {nums[1]}',
                    f'= {area}'
                ],
                'answer': str(area)
            }

    if 'perimeter' in problem_lower and 'rectangle' in problem_lower:
        nums = [int(n) for n in re.findall(r'\d+', problem)]
        if len(nums) >= 2:
            perimeter = 2 * (nums[0] + nums[1])
            return {
                'steps': [
                    f'Perimeter of a rectangle = 2 × (length + width)',
                    f'= 2 × ({nums[0]} + {nums[1]})',
                    f'= 2 × {nums[0] + nums[1]}',
                    f'= {perimeter}'
                ],
                'answer': str(perimeter)
            }

    return {'steps': ['Could not parse geometry problem.'], 'answer': 'Unknown'}


def _solve_quadratic(problem):
    """Solve a quadratic equation step by step."""
    import re
    try:
        from sympy import symbols, solve, Eq, sqrt as sym_sqrt
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        x = symbols('x')
        transforms = standard_transformations + (implicit_multiplication_application,)

        eq_str = problem.replace('Solve:', '').replace('Solve for x:', '').strip()
        eq_str = eq_str.replace('²', '**2')

        if '=' in eq_str:
            left, right = eq_str.split('=')
            left_expr = parse_expr(left.strip(), transformations=transforms)
            right_expr = parse_expr(right.strip(), transformations=transforms)
            solutions = solve(Eq(left_expr, right_expr), x)
        else:
            solutions = solve(parse_expr(eq_str, transformations=transforms), x)

        if not solutions:
            return {'steps': ['No real solutions found.'], 'answer': 'No solution'}

        steps = [
            f"Start with: {eq_str}",
            "Use the quadratic formula: x = (-b ± √(b²-4ac)) / 2a",
        ]

        answer_parts = [f"x = {s}" for s in solutions]
        answer = ', '.join(answer_parts)
        steps.append(f"Solutions: {answer}")

        return {'steps': steps, 'answer': answer}
    except Exception as e:
        return {'steps': [f'Could not solve: {e}'], 'answer': 'Unknown'}


def _solve_trig(problem):
    """Solve basic trig value problems step by step."""
    import math
    problem_lower = problem.lower()

    for func in ['sin', 'cos', 'tan']:
        match = re.search(rf'{func}\s*\(\s*(\d+)\s*°?\s*\)', problem_lower)
        if match:
            angle = int(match.group(1))
            rad = math.radians(angle)
            if func == 'sin':
                val = round(math.sin(rad), 6)
            elif func == 'cos':
                val = round(math.cos(rad), 6)
            else:
                if angle % 180 == 90:
                    return {'steps': [f'{func}({angle}°) is undefined'], 'answer': 'undefined'}
                val = round(math.tan(rad), 6)

            steps = [
                f"Find {func}({angle}°)",
                f"Convert to radians: {angle}° = {round(rad, 4)} radians",
                f"{func}({angle}°) = {val}"
            ]
            return {'steps': steps, 'answer': str(val)}

    return {'steps': ['Could not parse trig problem.'], 'answer': 'Unknown'}


def _solve_logarithm(problem):
    """Solve logarithm problems step by step."""
    import math

    # Match log_base(argument) patterns
    match = re.search(r'log[_]?\s*(\d+)\s*\(\s*(\d+)\s*\)', problem)
    if match:
        base = int(match.group(1))
        arg = int(match.group(2))
        result = round(math.log(arg) / math.log(base), 6)

        steps = [
            f"Evaluate log_{base}({arg})",
            f"Ask: {base} raised to what power equals {arg}?",
        ]

        if result == int(result):
            result = int(result)
            steps.append(f"{base}^{result} = {arg}")
            steps.append(f"Answer: {result}")
        else:
            steps.append(f"log_{base}({arg}) ≈ {result}")

        return {'steps': steps, 'answer': str(result)}

    # Natural log
    match = re.search(r'ln\s*\(\s*(\d+\.?\d*)\s*\)', problem)
    if match:
        arg = float(match.group(1))
        result = round(math.log(arg), 6)
        steps = [
            f"Evaluate ln({arg})",
            f"ln({arg}) ≈ {result}"
        ]
        return {'steps': steps, 'answer': str(result)}

    return {'steps': ['Could not parse logarithm problem.'], 'answer': 'Unknown'}
