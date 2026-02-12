"""Trigonometry operations - sin, cos, tan, unit circle, law of sines/cosines (grades 10-12)."""

import random
import math
from fractions import Fraction


# Common angles and their exact trig values
UNIT_CIRCLE = {
    0:   {'sin': Fraction(0), 'cos': Fraction(1), 'tan': Fraction(0)},
    30:  {'sin': Fraction(1, 2), 'cos': 'sqrt(3)/2', 'tan': 'sqrt(3)/3'},
    45:  {'sin': 'sqrt(2)/2', 'cos': 'sqrt(2)/2', 'tan': Fraction(1)},
    60:  {'sin': 'sqrt(3)/2', 'cos': Fraction(1, 2), 'tan': 'sqrt(3)'},
    90:  {'sin': Fraction(1), 'cos': Fraction(0), 'tan': 'undefined'},
    120: {'sin': 'sqrt(3)/2', 'cos': Fraction(-1, 2), 'tan': '-sqrt(3)'},
    135: {'sin': 'sqrt(2)/2', 'cos': '-sqrt(2)/2', 'tan': Fraction(-1)},
    150: {'sin': Fraction(1, 2), 'cos': '-sqrt(3)/2', 'tan': '-sqrt(3)/3'},
    180: {'sin': Fraction(0), 'cos': Fraction(-1), 'tan': Fraction(0)},
    210: {'sin': Fraction(-1, 2), 'cos': '-sqrt(3)/2', 'tan': 'sqrt(3)/3'},
    225: {'sin': '-sqrt(2)/2', 'cos': '-sqrt(2)/2', 'tan': Fraction(1)},
    240: {'sin': '-sqrt(3)/2', 'cos': Fraction(-1, 2), 'tan': 'sqrt(3)'},
    270: {'sin': Fraction(-1), 'cos': Fraction(0), 'tan': 'undefined'},
    300: {'sin': '-sqrt(3)/2', 'cos': Fraction(1, 2), 'tan': '-sqrt(3)'},
    315: {'sin': '-sqrt(2)/2', 'cos': 'sqrt(2)/2', 'tan': Fraction(-1)},
    330: {'sin': Fraction(-1, 2), 'cos': 'sqrt(3)/2', 'tan': '-sqrt(3)/3'},
    360: {'sin': Fraction(0), 'cos': Fraction(1), 'tan': Fraction(0)},
}


def degrees_to_radians(degrees):
    """Convert degrees to radians as a fraction of pi."""
    return Fraction(degrees, 180)


def radians_to_degrees(rad_frac):
    """Convert a fraction-of-pi radians to degrees."""
    return float(rad_frac) * 180


def trig_value(func, angle_deg):
    """Get the trig value for a standard angle."""
    angle_deg = angle_deg % 360
    if angle_deg in UNIT_CIRCLE:
        return UNIT_CIRCLE[angle_deg].get(func, 'unknown')
    return round(getattr(math, func)(math.radians(angle_deg)), 4)


def law_of_cosines_side(a, b, angle_C_deg):
    """Find side c using law of cosines: c^2 = a^2 + b^2 - 2ab*cos(C)."""
    C = math.radians(angle_C_deg)
    c_squared = a**2 + b**2 - 2*a*b*math.cos(C)
    return round(math.sqrt(c_squared), 2)


def law_of_sines_angle(a, angle_A_deg, b):
    """Find angle B using law of sines: sin(B)/b = sin(A)/a."""
    A = math.radians(angle_A_deg)
    sin_B = b * math.sin(A) / a
    if abs(sin_B) > 1:
        return None
    return round(math.degrees(math.asin(sin_B)), 2)


def generate_unit_circle_problems(grade, count=5):
    """Generate unit circle / trig value problems."""
    problems = []
    common_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
    funcs = ['sin', 'cos', 'tan']

    for _ in range(count):
        angle = random.choice(common_angles)
        func = random.choice(funcs)
        val = UNIT_CIRCLE.get(angle, {}).get(func, 'unknown')
        answer = str(val)

        problems.append({
            'type': 'fill_in',
            'question': f'What is {func}({angle}°)?',
            'answer': answer,
            'hint': f'Think about the unit circle. What are the coordinates at {angle}°?'
        })
    return problems


def generate_radian_conversion(grade, count=5):
    """Generate degree-radian conversion problems."""
    problems = []
    angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]

    for _ in range(count):
        angle = random.choice(angles)
        if random.random() > 0.5:
            rad = degrees_to_radians(angle)
            if rad.denominator == 1:
                answer = f'{rad.numerator}pi' if rad.numerator != 0 else '0'
            else:
                answer = f'{rad.numerator}pi/{rad.denominator}'
            problems.append({
                'type': 'fill_in',
                'question': f'Convert {angle}° to radians.',
                'answer': answer,
                'hint': 'Multiply the degree measure by pi/180 and simplify.'
            })
        else:
            rad = degrees_to_radians(angle)
            if rad.denominator == 1:
                rad_str = f'{rad.numerator}π' if rad.numerator != 0 else '0'
            else:
                rad_str = f'{rad.numerator}π/{rad.denominator}'
            problems.append({
                'type': 'fill_in',
                'question': f'Convert {rad_str} radians to degrees.',
                'answer': str(angle),
                'hint': 'Multiply the radian measure by 180/pi.'
            })
    return problems


def generate_right_triangle_trig(grade, count=5):
    """Generate SOH-CAH-TOA problems with right triangles."""
    problems = []
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (7, 24, 25)]

    for _ in range(count):
        a, b, c = random.choice(triples)
        func = random.choice(['sin', 'cos', 'tan'])

        if func == 'sin':
            answer = f'{a}/{c}'
            problems.append({
                'type': 'fill_in',
                'question': f'In a right triangle with opposite side {a} and hypotenuse {c}, what is sin(θ)?',
                'answer': answer,
                'hint': 'SOH: Sin = Opposite / Hypotenuse'
            })
        elif func == 'cos':
            answer = f'{b}/{c}'
            problems.append({
                'type': 'fill_in',
                'question': f'In a right triangle with adjacent side {b} and hypotenuse {c}, what is cos(θ)?',
                'answer': answer,
                'hint': 'CAH: Cos = Adjacent / Hypotenuse'
            })
        else:
            answer = f'{a}/{b}'
            problems.append({
                'type': 'fill_in',
                'question': f'In a right triangle with opposite side {a} and adjacent side {b}, what is tan(θ)?',
                'answer': answer,
                'hint': 'TOA: Tan = Opposite / Adjacent'
            })
    return problems
