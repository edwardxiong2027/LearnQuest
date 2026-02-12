"""Problem generator - creates grade-appropriate math problems with verified answers (K-12)."""

from math_engine.arithmetic import (
    generate_addition, generate_subtraction,
    generate_multiplication, generate_division
)
from math_engine.fractions_ops import (
    generate_fraction_addition, generate_fraction_subtraction,
    generate_fraction_multiply
)
from math_engine.algebra import generate_linear_equations, generate_expression_evaluation
from math_engine.geometry import (
    generate_area_perimeter, generate_volume, generate_pythagorean,
    generate_circle_problems, generate_3d_problems
)
from math_engine.statistics import generate_statistics_problems, generate_advanced_statistics
from math_engine.trigonometry import (
    generate_unit_circle_problems, generate_radian_conversion,
    generate_right_triangle_trig
)
from math_engine.advanced_algebra import (
    generate_quadratic_problems, generate_system_problems,
    generate_polynomial_problems, generate_complex_number_problems
)
from math_engine.precalculus import (
    generate_logarithm_problems, generate_exponential_problems,
    generate_limit_problems, generate_matrix_problems,
    generate_vector_problems
)


TOPIC_GENERATORS = {
    'addition': generate_addition,
    'subtraction': generate_subtraction,
    'multiplication': generate_multiplication,
    'division': generate_division,
    'fraction_addition': generate_fraction_addition,
    'fraction_subtraction': generate_fraction_subtraction,
    'fraction_multiplication': generate_fraction_multiply,
    'linear_equations': generate_linear_equations,
    'expressions': generate_expression_evaluation,
    'area_perimeter': generate_area_perimeter,
    'volume': generate_volume,
    'statistics': generate_statistics_problems,
    'advanced_statistics': generate_advanced_statistics,
    'unit_circle': generate_unit_circle_problems,
    'radian_conversion': generate_radian_conversion,
    'right_triangle_trig': generate_right_triangle_trig,
    'quadratics': generate_quadratic_problems,
    'systems': generate_system_problems,
    'polynomials': generate_polynomial_problems,
    'complex_numbers': generate_complex_number_problems,
    'logarithms': generate_logarithm_problems,
    'exponentials': generate_exponential_problems,
    'limits': generate_limit_problems,
    'matrices': generate_matrix_problems,
    'vectors': generate_vector_problems,
    'circles': generate_circle_problems,
    '3d_geometry': generate_3d_problems,
}


def generate_problems(topic, grade, count=5):
    """Generate math problems for a given topic and grade."""
    topic = topic.lower().replace(' ', '_').replace('-', '_')

    # Map common topic names to generators
    topic_map = {
        'add': 'addition',
        'subtract': 'subtraction',
        'multiply': 'multiplication',
        'divide': 'division',
        'fractions': 'fraction_addition',
        'fraction_add': 'fraction_addition',
        'fraction_sub': 'fraction_subtraction',
        'fraction_mult': 'fraction_multiplication',
        'algebra': 'linear_equations',
        'equations': 'linear_equations',
        'geometry': 'area_perimeter',
        'area': 'area_perimeter',
        'perimeter': 'area_perimeter',
        'pythagorean': 'pythagorean',
        'stats': 'statistics',
        'mean': 'statistics',
        'median': 'statistics',
        'trig': 'unit_circle',
        'trigonometry': 'unit_circle',
        'sin': 'right_triangle_trig',
        'cos': 'right_triangle_trig',
        'tan': 'right_triangle_trig',
        'quadratic': 'quadratics',
        'factoring': 'quadratics',
        'system': 'systems',
        'systems_of_equations': 'systems',
        'polynomial': 'polynomials',
        'complex': 'complex_numbers',
        'log': 'logarithms',
        'logarithm': 'logarithms',
        'exponential': 'exponentials',
        'limit': 'limits',
        'matrix': 'matrices',
        'vector': 'vectors',
        'circle': 'circles',
        'sphere': '3d_geometry',
        'cone': '3d_geometry',
        'cylinder': '3d_geometry',
        'standard_deviation': 'advanced_statistics',
        'probability': 'advanced_statistics',
        'combinations': 'advanced_statistics',
        'permutations': 'advanced_statistics',
    }

    resolved_topic = topic_map.get(topic, topic)

    if resolved_topic == 'pythagorean':
        return generate_pythagorean(count)

    generator = TOPIC_GENERATORS.get(resolved_topic)
    if not generator:
        return _generate_grade_mix(grade, count)

    return generator(grade, count)


def _generate_grade_mix(grade, count):
    """Generate a mix of problems appropriate for the grade level."""
    import random

    if grade <= 2:
        topics = ['addition', 'subtraction']
    elif grade <= 4:
        topics = ['addition', 'subtraction', 'multiplication', 'division']
    elif grade <= 5:
        topics = ['multiplication', 'division', 'fraction_addition', 'area_perimeter']
    elif grade <= 6:
        topics = ['fraction_addition', 'fraction_multiplication', 'linear_equations', 'area_perimeter']
    elif grade <= 8:
        topics = ['linear_equations', 'expressions', 'statistics', 'area_perimeter']
    elif grade == 9:
        topics = ['linear_equations', 'quadratics', 'systems', 'polynomials']
    elif grade == 10:
        topics = ['right_triangle_trig', 'circles', 'area_perimeter', '3d_geometry']
    elif grade == 11:
        topics = ['quadratics', 'unit_circle', 'logarithms', 'advanced_statistics']
    else:  # grade 12
        topics = ['limits', 'logarithms', 'vectors', 'matrices']

    problems = []
    per_topic = max(1, count // len(topics))

    for topic in topics:
        gen = TOPIC_GENERATORS.get(topic)
        if gen:
            problems.extend(gen(grade, per_topic))

    random.shuffle(problems)
    return problems[:count]
