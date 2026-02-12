"""Statistics operations - mean, median, mode, range, std dev, probability, combinatorics (grades 6-12)."""

import random
import math
from fractions import Fraction


def mean(numbers):
    """Calculate the mean of a list of numbers."""
    if not numbers:
        return 0
    return sum(Fraction(n) for n in numbers) / len(numbers)


def median(numbers):
    """Calculate the median of a list of numbers."""
    if not numbers:
        return 0
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n % 2 == 1:
        return sorted_nums[n // 2]
    else:
        return (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2


def mode(numbers):
    """Calculate the mode of a list of numbers."""
    if not numbers:
        return 0
    from collections import Counter
    counter = Counter(numbers)
    max_count = max(counter.values())
    modes = [k for k, v in counter.items() if v == max_count]
    return min(modes)  # Return smallest mode if multiple


def range_of(numbers):
    """Calculate the range of a list of numbers."""
    if not numbers:
        return 0
    return max(numbers) - min(numbers)


def generate_statistics_problems(grade, count=5):
    """Generate statistics problems."""
    problems = []
    for _ in range(count):
        # Generate a dataset
        size = random.randint(5, 9)
        if grade <= 6:
            data = [random.randint(1, 20) for _ in range(size)]
        else:
            data = [random.randint(1, 100) for _ in range(size)]

        data_str = ', '.join(str(d) for d in data)
        stat_type = random.choice(['mean', 'median', 'mode', 'range'])

        if stat_type == 'mean':
            result = mean(data)
            # Format nicely
            if result.denominator == 1:
                answer = str(result.numerator)
            else:
                answer = str(round(float(result), 2))
            problems.append({
                'type': 'fill_in',
                'question': f'Find the mean (average) of: {data_str}',
                'answer': answer,
                'hint': 'Add all the numbers together, then divide by how many numbers there are.'
            })
        elif stat_type == 'median':
            result = median(data)
            answer = str(result) if isinstance(result, int) else str(round(float(result), 1))
            problems.append({
                'type': 'fill_in',
                'question': f'Find the median of: {data_str}',
                'answer': answer,
                'hint': 'First arrange the numbers in order, then find the middle value.'
            })
        elif stat_type == 'mode':
            # Make sure there IS a clear mode
            data.append(random.choice(data))
            data_str = ', '.join(str(d) for d in data)
            result = mode(data)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the mode of: {data_str}',
                'answer': str(result),
                'hint': 'The mode is the number that appears most often.'
            })
        elif stat_type == 'range':
            result = range_of(data)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the range of: {data_str}',
                'answer': str(result),
                'hint': 'Range = largest number - smallest number'
            })

    return problems


def standard_deviation(numbers):
    """Calculate population standard deviation."""
    if len(numbers) < 2:
        return 0
    avg = sum(numbers) / len(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
    return round(math.sqrt(variance), 4)


def factorial(n):
    """Compute n!"""
    return math.factorial(n)


def permutation(n, r):
    """Compute P(n,r) = n!/(n-r)!"""
    return math.factorial(n) // math.factorial(n - r)


def combination(n, r):
    """Compute C(n,r) = n!/(r!(n-r)!)"""
    return math.comb(n, r)


def generate_advanced_statistics(grade, count=5):
    """Generate advanced statistics problems (grades 9-12)."""
    problems = []
    for _ in range(count):
        prob_type = random.choice(['std_dev', 'probability', 'combination', 'permutation'])

        if prob_type == 'std_dev':
            size = random.randint(5, 7)
            data = [random.randint(10, 50) for _ in range(size)]
            data_str = ', '.join(str(d) for d in data)
            sd = standard_deviation(data)
            problems.append({
                'type': 'fill_in',
                'question': f'Find the population standard deviation of: {data_str}. Round to 4 decimal places.',
                'answer': str(sd),
                'hint': 'First find the mean, then compute the average of squared deviations, then take the square root.'
            })
        elif prob_type == 'probability':
            total = random.choice([6, 10, 12, 20, 52])
            favorable = random.randint(1, total - 1)
            frac = Fraction(favorable, total)
            scenarios = {
                6: f'rolling a number less than {favorable + 1} on a standard die',
                10: f'drawing one of {favorable} specific items from a bag of {total}',
                12: f'selecting one of {favorable} months from the year',
                20: f'picking one of {favorable} specific students from a class of {total}',
                52: f'drawing one of {favorable} specific cards from a standard deck',
            }
            problems.append({
                'type': 'fill_in',
                'question': f'What is the probability of {scenarios[total]}?',
                'answer': str(frac),
                'hint': 'Probability = favorable outcomes / total outcomes'
            })
        elif prob_type == 'combination':
            n = random.randint(5, 10)
            r = random.randint(2, min(4, n))
            answer = combination(n, r)
            problems.append({
                'type': 'fill_in',
                'question': f'Calculate C({n}, {r}) (combinations of {n} choose {r}).',
                'answer': str(answer),
                'hint': 'C(n,r) = n! / (r!(n-r)!). Order does not matter.'
            })
        else:
            n = random.randint(4, 8)
            r = random.randint(2, min(3, n))
            answer = permutation(n, r)
            problems.append({
                'type': 'fill_in',
                'question': f'Calculate P({n}, {r}) (permutations of {n} taken {r} at a time).',
                'answer': str(answer),
                'hint': 'P(n,r) = n! / (n-r)!. Order matters.'
            })

    return problems
