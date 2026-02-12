"""Geometry operations - area, perimeter, volume for basic and advanced shapes (K-12)."""

import random
import math


def area_rectangle(length, width):
    return length * width


def perimeter_rectangle(length, width):
    return 2 * (length + width)


def area_triangle(base, height):
    return 0.5 * base * height


def area_circle(radius):
    return math.pi * radius ** 2


def circumference_circle(radius):
    return 2 * math.pi * radius


def volume_rectangular_prism(length, width, height):
    return length * width * height


def volume_cylinder(radius, height):
    return math.pi * radius ** 2 * height


def surface_area_rectangular_prism(length, width, height):
    return 2 * (length * width + width * height + length * height)


def pythagorean(a=None, b=None, c=None):
    """Given two sides of a right triangle, find the third."""
    if c is None:
        return math.sqrt(a**2 + b**2)
    elif a is None:
        return math.sqrt(c**2 - b**2)
    elif b is None:
        return math.sqrt(c**2 - a**2)


def generate_area_perimeter(grade, count=5):
    """Generate area/perimeter problems."""
    problems = []
    for _ in range(count):
        shape = random.choice(['rectangle', 'square', 'triangle'])

        if shape == 'rectangle':
            l = random.randint(2, 15)
            w = random.randint(2, 15)
            if random.random() > 0.5:
                # Area
                answer = l * w
                problems.append({
                    'type': 'fill_in',
                    'question': f'What is the area of a rectangle with length {l} and width {w}?',
                    'answer': str(answer),
                    'hint': 'Area of a rectangle = length × width'
                })
            else:
                # Perimeter
                answer = 2 * (l + w)
                problems.append({
                    'type': 'fill_in',
                    'question': f'What is the perimeter of a rectangle with length {l} and width {w}?',
                    'answer': str(answer),
                    'hint': 'Perimeter = 2 × (length + width)'
                })
        elif shape == 'square':
            s = random.randint(2, 15)
            if random.random() > 0.5:
                answer = s * s
                problems.append({
                    'type': 'fill_in',
                    'question': f'What is the area of a square with side length {s}?',
                    'answer': str(answer),
                    'hint': 'Area of a square = side × side'
                })
            else:
                answer = 4 * s
                problems.append({
                    'type': 'fill_in',
                    'question': f'What is the perimeter of a square with side length {s}?',
                    'answer': str(answer),
                    'hint': 'Perimeter of a square = 4 × side'
                })
        elif shape == 'triangle':
            base = random.randint(2, 15)
            height = random.randint(2, 15)
            area = base * height / 2
            answer = str(int(area)) if area == int(area) else str(area)
            problems.append({
                'type': 'fill_in',
                'question': f'What is the area of a triangle with base {base} and height {height}?',
                'answer': answer,
                'hint': 'Area of a triangle = (base × height) ÷ 2'
            })

    return problems


def generate_volume(grade, count=5):
    """Generate volume problems (grades 5+)."""
    problems = []
    for _ in range(count):
        l = random.randint(2, 10)
        w = random.randint(2, 10)
        h = random.randint(2, 10)
        vol = l * w * h
        problems.append({
            'type': 'fill_in',
            'question': f'What is the volume of a rectangular prism with length {l}, width {w}, and height {h}?',
            'answer': str(vol),
            'hint': 'Volume = length × width × height'
        })
    return problems


def generate_pythagorean(count=5):
    """Generate Pythagorean theorem problems (grade 8+)."""
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (9, 12, 15), (7, 24, 25)]
    problems = []
    for _ in range(count):
        a, b, c = random.choice(triples)
        which = random.choice(['c', 'a', 'b'])
        if which == 'c':
            problems.append({
                'type': 'fill_in',
                'question': f'A right triangle has legs of length {a} and {b}. What is the length of the hypotenuse?',
                'answer': str(c),
                'hint': 'Use the Pythagorean theorem: a² + b² = c²'
            })
        elif which == 'a':
            problems.append({
                'type': 'fill_in',
                'question': f'A right triangle has one leg of {b} and hypotenuse of {c}. What is the other leg?',
                'answer': str(a),
                'hint': 'Rearrange: a² = c² - b²'
            })
        else:
            problems.append({
                'type': 'fill_in',
                'question': f'A right triangle has one leg of {a} and hypotenuse of {c}. What is the other leg?',
                'answer': str(b),
                'hint': 'Rearrange: b² = c² - a²'
            })
    return problems


def area_circle_sector(radius, angle_deg):
    """Area of a circular sector."""
    return (angle_deg / 360) * math.pi * radius ** 2


def arc_length(radius, angle_deg):
    """Arc length of a circular sector."""
    return (angle_deg / 360) * 2 * math.pi * radius


def volume_cone(radius, height):
    return (1/3) * math.pi * radius ** 2 * height


def volume_sphere(radius):
    return (4/3) * math.pi * radius ** 3


def surface_area_sphere(radius):
    return 4 * math.pi * radius ** 2


def generate_circle_problems(grade, count=5):
    """Generate circle geometry problems (grade 10+)."""
    problems = []
    for _ in range(count):
        r = random.randint(2, 10)
        prob = random.choice(['area', 'circumference', 'arc_length', 'sector_area'])

        if prob == 'area':
            answer = round(math.pi * r**2, 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the area of a circle with radius {r}. Round to 2 decimal places.',
                'answer': str(answer),
                'hint': 'Area = πr²'
            })
        elif prob == 'circumference':
            answer = round(2 * math.pi * r, 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the circumference of a circle with radius {r}. Round to 2 decimal places.',
                'answer': str(answer),
                'hint': 'Circumference = 2πr'
            })
        elif prob == 'arc_length':
            angle = random.choice([30, 45, 60, 90, 120, 180])
            answer = round(arc_length(r, angle), 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the arc length of a sector with radius {r} and central angle {angle}°. Round to 2 decimal places.',
                'answer': str(answer),
                'hint': 'Arc length = (angle/360) × 2πr'
            })
        else:
            angle = random.choice([30, 45, 60, 90, 120, 180])
            answer = round(area_circle_sector(r, angle), 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the area of a sector with radius {r} and central angle {angle}°. Round to 2 decimal places.',
                'answer': str(answer),
                'hint': 'Sector area = (angle/360) × πr²'
            })
    return problems


def generate_3d_problems(grade, count=5):
    """Generate 3D volume/surface area problems (grade 10+)."""
    problems = []
    for _ in range(count):
        shape = random.choice(['cone', 'sphere', 'cylinder'])

        if shape == 'cone':
            r = random.randint(2, 8)
            h = random.randint(3, 12)
            vol = round(volume_cone(r, h), 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the volume of a cone with radius {r} and height {h}. Round to 2 decimal places.',
                'answer': str(vol),
                'hint': 'Volume of cone = (1/3)πr²h'
            })
        elif shape == 'sphere':
            r = random.randint(2, 8)
            if random.random() > 0.5:
                vol = round(volume_sphere(r), 2)
                problems.append({
                    'type': 'fill_in',
                    'question': f'Find the volume of a sphere with radius {r}. Round to 2 decimal places.',
                    'answer': str(vol),
                    'hint': 'Volume of sphere = (4/3)πr³'
                })
            else:
                sa = round(surface_area_sphere(r), 2)
                problems.append({
                    'type': 'fill_in',
                    'question': f'Find the surface area of a sphere with radius {r}. Round to 2 decimal places.',
                    'answer': str(sa),
                    'hint': 'Surface area of sphere = 4πr²'
                })
        else:
            r = random.randint(2, 8)
            h = random.randint(3, 12)
            vol = round(volume_cylinder(r, h), 2)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the volume of a cylinder with radius {r} and height {h}. Round to 2 decimal places.',
                'answer': str(vol),
                'hint': 'Volume of cylinder = πr²h'
            })
    return problems
