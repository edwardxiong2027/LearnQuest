"""Fraction operations - add, subtract, multiply, divide, simplify, compare."""

import random
from fractions import Fraction


def add_fractions(a_num, a_den, b_num, b_den):
    """Add two fractions and return simplified result."""
    result = Fraction(a_num, a_den) + Fraction(b_num, b_den)
    return result


def subtract_fractions(a_num, a_den, b_num, b_den):
    result = Fraction(a_num, a_den) - Fraction(b_num, b_den)
    return result


def multiply_fractions(a_num, a_den, b_num, b_den):
    result = Fraction(a_num, a_den) * Fraction(b_num, b_den)
    return result


def divide_fractions(a_num, a_den, b_num, b_den):
    result = Fraction(a_num, a_den) / Fraction(b_num, b_den)
    return result


def simplify_fraction(num, den):
    f = Fraction(num, den)
    return f


def format_fraction(f):
    """Format a Fraction as a string, handling mixed numbers."""
    if f.denominator == 1:
        return str(f.numerator)
    if abs(f.numerator) > f.denominator:
        whole = f.numerator // f.denominator
        remainder = abs(f.numerator) % f.denominator
        if remainder == 0:
            return str(whole)
        return f"{whole} {remainder}/{f.denominator}"
    return f"{f.numerator}/{f.denominator}"


def parse_fraction_str(s):
    """Parse a fraction string like '3/4', '1 1/2', '0.5' into a Fraction."""
    s = s.strip()

    # Handle decimal
    if '.' in s and '/' not in s:
        return Fraction(s).limit_denominator(10000)

    # Handle mixed number: "1 3/4"
    parts = s.split()
    if len(parts) == 2 and '/' in parts[1]:
        whole = int(parts[0])
        frac_parts = parts[1].split('/')
        num, den = int(frac_parts[0]), int(frac_parts[1])
        sign = -1 if whole < 0 else 1
        return Fraction(sign * (abs(whole) * den + num), den)

    # Handle simple fraction: "3/4"
    if '/' in s:
        parts = s.split('/')
        return Fraction(int(parts[0]), int(parts[1]))

    # Handle whole number
    return Fraction(int(s))


def generate_fraction_addition(grade, count=5):
    """Generate fraction addition problems."""
    problems = []
    for _ in range(count):
        if grade <= 4:
            # Same denominator
            den = random.choice([2, 3, 4, 5, 6, 8])
            a_num = random.randint(1, den - 1)
            b_num = random.randint(1, den - 1)
            a_den = b_den = den
        else:
            # Different denominators
            a_den = random.choice([2, 3, 4, 5, 6, 8])
            b_den = random.choice([2, 3, 4, 5, 6, 8])
            a_num = random.randint(1, a_den - 1)
            b_num = random.randint(1, b_den - 1)

        result = add_fractions(a_num, a_den, b_num, b_den)
        answer_str = format_fraction(result)

        problems.append({
            'type': 'fill_in',
            'question': f'What is {a_num}/{a_den} + {b_num}/{b_den}?',
            'answer': answer_str,
            'operation': f'Fraction({a_num},{a_den}) + Fraction({b_num},{b_den})',
            'hint': f'Find a common denominator first. Try {a_den * b_den // _gcd(a_den, b_den)}.'
        })
    return problems


def generate_fraction_subtraction(grade, count=5):
    """Generate fraction subtraction problems."""
    problems = []
    for _ in range(count):
        den = random.choice([2, 3, 4, 5, 6, 8])
        a_num = random.randint(2, den)
        b_num = random.randint(1, a_num - 1)

        if grade >= 5 and random.random() > 0.5:
            b_den = random.choice([2, 3, 4, 5, 6, 8])
        else:
            b_den = den

        result = subtract_fractions(a_num, den, b_num, b_den)
        if result < 0:
            a_num, b_num = b_num, a_num  # Swap to keep positive
            result = subtract_fractions(a_num, den, b_num, b_den)

        answer_str = format_fraction(result)

        problems.append({
            'type': 'fill_in',
            'question': f'What is {a_num}/{den} - {b_num}/{b_den}?',
            'answer': answer_str,
            'hint': 'Make sure both fractions have the same denominator before subtracting.'
        })
    return problems


def generate_fraction_multiply(grade, count=5):
    """Generate fraction multiplication problems."""
    problems = []
    for _ in range(count):
        a_den = random.choice([2, 3, 4, 5, 6])
        b_den = random.choice([2, 3, 4, 5, 6])
        a_num = random.randint(1, a_den)
        b_num = random.randint(1, b_den)

        result = multiply_fractions(a_num, a_den, b_num, b_den)
        answer_str = format_fraction(result)

        problems.append({
            'type': 'fill_in',
            'question': f'What is {a_num}/{a_den} × {b_num}/{b_den}?',
            'answer': answer_str,
            'hint': 'Multiply the numerators together, then multiply the denominators.'
        })
    return problems


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a
