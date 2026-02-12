"""Answer validator - checks student answers against correct answers with tolerance for equivalent forms."""

from fractions import Fraction
import re


def validate_answer(student_answer, correct_answer):
    """
    Check if a student's answer is equivalent to the correct answer.
    Handles: integers, decimals, fractions, mixed numbers, and equivalent forms.
    E.g., '1/2' = '2/4' = '0.5' = '.5'
    """
    student_answer = str(student_answer).strip()
    correct_answer = str(correct_answer).strip()

    # Direct string match (case-insensitive)
    if student_answer.lower() == correct_answer.lower():
        return True

    # Try numeric comparison
    try:
        student_val = _parse_number(student_answer)
        correct_val = _parse_number(correct_answer)

        if student_val is not None and correct_val is not None:
            # Compare as Fractions for exact match
            if student_val == correct_val:
                return True

            # Floating point tolerance for decimals
            if abs(float(student_val) - float(correct_val)) < 0.001:
                return True
    except (ValueError, ZeroDivisionError, OverflowError):
        pass

    return False


def _parse_number(s):
    """Parse a string into a Fraction. Handles various formats."""
    s = s.strip()

    if not s:
        return None

    # Remove commas in numbers (e.g., "1,000")
    s = s.replace(',', '')

    # Handle percentage
    if s.endswith('%'):
        try:
            return Fraction(s[:-1].strip()) / 100
        except:
            return None

    # Handle mixed number: "1 3/4" or "1 and 3/4"
    mixed_match = re.match(r'^(-?\d+)\s+(\d+)\s*/\s*(\d+)$', s)
    if mixed_match:
        whole = int(mixed_match.group(1))
        num = int(mixed_match.group(2))
        den = int(mixed_match.group(3))
        if den == 0:
            return None
        sign = -1 if whole < 0 else 1
        return Fraction(sign * (abs(whole) * den + num), den)

    # Handle fraction: "3/4"
    frac_match = re.match(r'^(-?\d+)\s*/\s*(\d+)$', s)
    if frac_match:
        num = int(frac_match.group(1))
        den = int(frac_match.group(2))
        if den == 0:
            return None
        return Fraction(num, den)

    # Handle decimal: "3.14", ".5"
    decimal_match = re.match(r'^-?\d*\.?\d+$', s)
    if decimal_match:
        return Fraction(s).limit_denominator(100000)

    # Handle integer
    try:
        return Fraction(int(s))
    except ValueError:
        pass

    # Handle pi-based answers (e.g., "4π", "4pi")
    pi_match = re.match(r'^(-?\d*\.?\d*)\s*[πpi]+$', s, re.IGNORECASE)
    if pi_match:
        coeff = pi_match.group(1)
        if not coeff or coeff == '-':
            coeff = coeff + '1' if coeff else '1'
        try:
            import math
            return Fraction(float(coeff) * math.pi).limit_denominator(100000)
        except:
            return None

    # Handle complex numbers (e.g., "3 + 2i", "3+2i", "-1 - 4i")
    complex_match = re.match(r'^(-?\d*\.?\d*)\s*([+-])\s*(\d*\.?\d*)i$', s)
    if complex_match:
        real = complex_match.group(1)
        sign = complex_match.group(2)
        imag = complex_match.group(3)
        try:
            real_val = float(real) if real else 0
            imag_val = float(imag) if imag else 1
            if sign == '-':
                imag_val = -imag_val
            return complex(real_val, imag_val)
        except:
            return None

    # Handle sqrt expressions (e.g., "sqrt(2)", "2sqrt(3)")
    sqrt_match = re.match(r'^(-?\d*\.?\d*)\s*sqrt\((\d+)\)(?:\s*/\s*(\d+))?$', s, re.IGNORECASE)
    if sqrt_match:
        coeff = sqrt_match.group(1)
        radicand = int(sqrt_match.group(2))
        denom = sqrt_match.group(3)
        try:
            import math
            coeff_val = float(coeff) if coeff and coeff != '-' else (-1 if coeff == '-' else 1)
            result = coeff_val * math.sqrt(radicand)
            if denom:
                result /= int(denom)
            return Fraction(result).limit_denominator(100000)
        except:
            return None

    # Handle vector notation (e.g., "<3, 4>")
    vector_match = re.match(r'^<\s*(-?\d+)\s*,\s*(-?\d+)\s*>$', s)
    if vector_match:
        return s  # Return as-is for string comparison

    # Handle interval notation (e.g., "(-2, 5]")
    interval_match = re.match(r'^[\[\(]-?\d+\.?\d*\s*,\s*-?\d+\.?\d*[\]\)]$', s)
    if interval_match:
        return s  # Return as-is for string comparison

    return None
