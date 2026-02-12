"""AI Studio content generation routes with programmatic fallback."""

import os
import json
import random
from flask import Blueprint, request, jsonify, session, current_app
from api.llm_utils import load_prompt, call_ollama, parse_json_response, \
    get_cached_response, cache_response, make_cache_key

generate_bp = Blueprint('generate', __name__)


def get_db():
    return current_app.get_db()


def require_auth():
    if 'user_id' not in session:
        return None
    return session['user_id']


# ---------------------------------------------------------------------------
# Topic presets by subject and grade band
# ---------------------------------------------------------------------------

TOPIC_PRESETS = {
    'math': {
        'k': ['Counting to 10', 'Counting to 20', 'Number Recognition', 'Basic Addition', 'Basic Subtraction', 'Shapes', 'Comparing Sizes', 'Patterns', 'Sorting', 'More and Less'],
        '1': ['Addition within 20', 'Subtraction within 20', 'Place Value (Tens and Ones)', 'Measuring Lengths', 'Telling Time', 'Shapes and Fractions', 'Halves and Quarters', 'Comparing Numbers', 'Number Patterns', 'Word Problems'],
        '2': ['Addition within 100', 'Subtraction within 100', 'Intro to Multiplication', 'Measuring in Standard Units', 'Money', 'Bar Graphs', 'Geometry', 'Even and Odd Numbers', 'Skip Counting', 'Time and Calendars'],
        '3': ['Multiplication Facts', 'Division Facts', 'Fractions on Number Line', 'Comparing Fractions', 'Area and Perimeter', 'Elapsed Time', 'Rounding Numbers', 'Bar and Picture Graphs', 'Multiplication Word Problems', 'Fraction Equivalence'],
        '4': ['Multi-digit Multiplication', 'Long Division', 'Fraction Equivalence', 'Adding Fractions', 'Decimals Introduction', 'Angles and Measurement', 'Line Plots', 'Factors and Multiples', 'Place Value to Millions', 'Fraction to Decimal Conversion'],
        '5': ['Adding and Subtracting Fractions', 'Multiplying Fractions', 'Decimal Operations', 'Volume', 'Coordinate Plane', 'Order of Operations', 'Dividing Fractions', 'Numerical Expressions', 'Converting Measurements', 'Powers of 10'],
        '6': ['Ratios and Proportions', 'Dividing Fractions', 'Integers and Rational Numbers', 'Expressions and Equations', 'Area and Surface Area', 'Volume', 'Statistics (Mean, Median, Mode)', 'Coordinate Graphing', 'Percent Problems', 'Absolute Value'],
        '7': ['Proportional Relationships', 'Operations with Rational Numbers', 'Expressions and Equations', 'Geometry (Scale, Circles, Angles)', 'Probability', 'Statistics and Sampling', 'Inequalities', 'Unit Rates', 'Circumference and Area of Circles', 'Cross Sections'],
        '8': ['Linear Equations', 'Functions', 'Pythagorean Theorem', 'Transformations', 'Scatter Plots', 'Exponents', 'Irrational Numbers', 'Systems of Equations', 'Scientific Notation', 'Slope and Intercept'],
    },
    'science': {
        'k': ['Five Senses', 'Animals', 'Plants', 'Weather', 'Seasons', 'Day and Night', 'Living vs Non-Living', 'Water', 'Push and Pull', 'Habitats'],
        '1': ['Animal Habitats', 'Plant Parts', 'Seasons and Weather', 'Sun and Moon', 'Light and Sound', 'Solids, Liquids, Gases', 'Animal Groups', 'Needs of Living Things', 'Earth Materials', 'Patterns in Nature'],
        '2': ['Life Cycles', 'States of Matter', 'Landforms', 'Weather Patterns', 'Food Chains', 'Insects', 'Magnets', 'Water Cycle Basics', 'Rocks and Soil', 'Plant Growth'],
        '3': ['Ecosystems', 'Life Cycles', 'Rock Cycle', 'Weather and Climate', 'Forces and Motion', 'Inherited Traits', 'Fossils', 'Simple Machines', 'Adaptations', 'Sound Waves'],
        '4': ['Energy Forms', 'Electricity', 'Ecosystems and Food Webs', 'Earth\'s Surface Changes', 'Weathering and Erosion', 'Properties of Matter', 'Light and Optics', 'Animal Adaptations', 'Water Cycle', 'Renewable Energy'],
        '5': ['Solar System', 'Properties of Matter', 'Chemical Changes', 'Ecosystems', 'Water Cycle', 'Simple Machines and Energy', 'Earth\'s Layers', 'Stars and Constellations', 'Mixtures and Solutions', 'Gravity'],
        '6': ['Cells and Cell Theory', 'Body Systems', 'Atoms and Elements', 'Periodic Table', 'Plate Tectonics', 'Climate and Weather', 'Energy Transfer', 'Photosynthesis', 'Classification of Life', 'Scientific Method'],
        '7': ['Genetics Basics', 'DNA and Heredity', 'Chemical Reactions', 'Forces and Motion', 'Waves and Sound', 'Earth\'s Atmosphere', 'Ecology and Biomes', 'Evolution Basics', 'Thermal Energy', 'Electromagnetic Spectrum'],
        '8': ['Physics: Motion and Forces', 'Chemistry: Reactions and Equations', 'Electricity and Magnetism', 'Earth Science: Climate Change', 'Astronomy', 'Human Body Systems', 'Atomic Structure', 'Conservation of Energy', 'Natural Selection', 'Renewable vs Non-Renewable Resources'],
    },
    'ela': {
        'k': ['Alphabet Letters', 'Phonics Basics', 'Sight Words', 'Rhyming Words', 'Story Retelling', 'Sentence Basics', 'Uppercase and Lowercase', 'Print Awareness', 'Vocabulary Building', 'Listening Skills'],
        '1': ['Phonics and Decoding', 'Sight Words Practice', 'Reading Comprehension', 'Sentence Structure', 'Capitalization', 'Punctuation Marks', 'Fiction vs Nonfiction', 'Story Elements', 'Writing Sentences', 'Vocabulary in Context'],
        '2': ['Reading Comprehension', 'Fiction and Nonfiction', 'Writing Paragraphs', 'Grammar Basics', 'Nouns and Verbs', 'Adjectives', 'Spelling Patterns', 'Narrative Writing', 'Main Idea and Details', 'Sequencing Events'],
        '3': ['Reading Comprehension Strategies', 'Paragraph Writing', 'Parts of Speech', 'Subject-Verb Agreement', 'Narrative Writing', 'Informational Text', 'Prefixes and Suffixes', 'Dictionary Skills', 'Point of View', 'Comparing Texts'],
        '4': ['Reading Comprehension', 'Essay Structure', 'Grammar and Mechanics', 'Persuasive Writing', 'Research Basics', 'Poetry Analysis', 'Figurative Language', 'Text Features', 'Summarizing', 'Verb Tenses'],
        '5': ['Literary Analysis', 'Expository Writing', 'Advanced Grammar', 'Research Papers', 'Vocabulary Building', 'Theme and Main Idea', 'Character Analysis', 'Argumentative Writing', 'Text Structure', 'Citing Sources'],
        '6': ['Literary Analysis', 'Argumentative Essays', 'Grammar and Mechanics', 'Vocabulary from Context', 'Research Writing', 'Rhetoric and Persuasion', 'Narrative Techniques', 'Figurative Language', 'Author\'s Purpose', 'Compare and Contrast Essays'],
        '7': ['Essay Writing', 'Literary Elements', 'Advanced Grammar', 'Vocabulary Building', 'Research Methods', 'Persuasive Techniques', 'Poetry Analysis', 'Informational Writing', 'Tone and Mood', 'Thesis Statements'],
        '8': ['Argumentative Writing', 'Literary Analysis', 'Research Papers', 'Advanced Vocabulary', 'Rhetoric', 'MLA Format', 'Critical Reading', 'Speech Writing', 'Narrative Craft', 'Analyzing Arguments'],
    },
    'social_studies': {
        'k': ['Community Helpers', 'Maps and Globes', 'US Symbols', 'Holidays', 'Families and Cultures', 'Rules and Laws', 'My Neighborhood', 'Needs and Wants', 'Good Citizenship', 'American Flag'],
        '1': ['Neighborhoods', 'Maps Skills', 'American Symbols', 'National Holidays', 'Community Workers', 'Rules and Responsibilities', 'Past and Present', 'Goods and Services', 'Landforms', 'Cultures Around the World'],
        '2': ['Communities', 'US Geography', 'Government Basics', 'Economics: Needs and Wants', 'History of Our Community', 'Famous Americans', 'Maps and Directions', 'World Cultures', 'Natural Resources', 'Traditions and Customs'],
        '3': ['Native Americans', 'Colonial America', 'American Revolution Basics', 'US Geography Regions', 'Local and State Government', 'Economics: Supply and Demand', 'Immigration', 'Map Skills', 'Explorers', 'Cultural Traditions'],
        '4': ['American Revolution', 'US Constitution', 'Westward Expansion', 'State History', 'Geography of the Americas', 'Economics', 'Government Branches', 'Civil Rights Basics', 'Maps and Regions', 'Slavery in America'],
        '5': ['Colonial America', 'American Revolution', 'Constitution and Bill of Rights', 'Westward Expansion', 'Civil War', 'Reconstruction', 'Industrial Revolution', 'Immigration Waves', 'Geography of US', 'Citizenship and Government'],
        '6': ['Ancient Civilizations', 'World Geography', 'Ancient Egypt', 'Ancient Greece', 'Ancient Rome', 'World Religions', 'Medieval Europe', 'African Kingdoms', 'Asian Civilizations', 'Trade Routes'],
        '7': ['World History: Middle Ages', 'Renaissance and Reformation', 'Age of Exploration', 'World Cultures', 'Economics Systems', 'Government Types', 'Imperialism', 'World Geography', 'Human Rights', 'Global Trade'],
        '8': ['US History: Civil War to Modern', 'World War I', 'World War II', 'Cold War', 'Civil Rights Movement', 'Modern America', 'US Government and Civics', 'Economics', 'Global Issues', 'Constitution Deep Dive'],
    }
}


def _get_topics_for(subject, grade):
    """Return topic presets for a given subject and grade."""
    grade_str = 'k' if grade == 0 else str(grade)
    subj_topics = TOPIC_PRESETS.get(subject, {})
    return subj_topics.get(grade_str, subj_topics.get('3', ['General Review']))


@generate_bp.route('/topics', methods=['GET'])
def get_topics():
    """Return topic presets for a subject/grade."""
    subject = request.args.get('subject', 'math')
    grade = int(request.args.get('grade', 3))
    return jsonify({'topics': _get_topics_for(subject, grade)})


# ---------------------------------------------------------------------------
# Curriculum-based fallback generation
# ---------------------------------------------------------------------------

def _load_curriculum(subject, grade):
    """Load curriculum JSON for a subject/grade."""
    content_dir = current_app.config['CONTENT_DIR']
    grade_str = 'k' if grade == 0 else str(grade)
    filepath = os.path.join(content_dir, subject, f'{grade_str}.json')
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _find_matching_lessons(data, topic):
    """Find lessons that match a topic string."""
    if not data:
        return []
    topic_lower = topic.lower()
    matches = []
    all_lessons = []
    for unit in data.get('units', []):
        for lesson in unit.get('lessons', []):
            all_lessons.append(lesson)
            title = (lesson.get('title', '') or '').lower()
            unit_title = (unit.get('title', '') or '').lower()
            explanation = (lesson.get('content', {}).get('explanation', '') or '').lower()
            if topic_lower in title or topic_lower in unit_title or topic_lower in explanation:
                matches.append(lesson)
    return matches if matches else all_lessons[:4]


def _fallback_lesson(subject, grade, topic):
    """Generate a lesson from curriculum data."""
    data = _load_curriculum(subject, grade)
    lessons = _find_matching_lessons(data, topic)
    if not lessons:
        return _generate_simple_lesson(subject, grade, topic)

    lesson = lessons[0]
    content = lesson.get('content', {})
    return {
        'title': f"{topic} — {lesson.get('title', 'Lesson')}",
        'explanation': content.get('explanation', f'Let\'s learn about {topic}!'),
        'examples': content.get('examples', []),
        'key_vocabulary': content.get('key_vocabulary', []),
        'real_world': content.get('real_world', ''),
        'practice_problems': lesson.get('practice_problems', [])[:5]
    }


def _generate_simple_lesson(subject, grade, topic):
    """Generate a minimal lesson when no curriculum data matches."""
    return {
        'title': topic,
        'explanation': f'This is a lesson about {topic} for grade {grade} {subject}. '
                       f'Learning about {topic} helps build important skills and understanding.',
        'examples': [],
        'key_vocabulary': [topic],
        'real_world': f'Understanding {topic} helps in many real-world situations.',
        'practice_problems': []
    }


def _fallback_flashcards(subject, grade, topic, count):
    """Generate flashcards from curriculum vocabulary and examples."""
    data = _load_curriculum(subject, grade)
    lessons = _find_matching_lessons(data, topic)
    cards = []

    for lesson in lessons:
        content = lesson.get('content', {})
        # Flashcards from vocabulary
        for word in content.get('key_vocabulary', []):
            cards.append({
                'front': f'What is "{word}"?',
                'back': f'A key term in {lesson.get("title", topic)} — {subject}',
                'hint': f'Related to {topic}'
            })
        # Flashcards from examples
        for ex in content.get('examples', []):
            if ex.get('problem') and ex.get('answer'):
                cards.append({
                    'front': str(ex['problem']),
                    'back': str(ex['answer']),
                    'hint': ex.get('explanation', '')[:80] if ex.get('explanation') else ''
                })
        # Flashcards from practice problems
        for prob in lesson.get('practice_problems', []):
            q = prob.get('question', '')
            a = prob.get('answer', '')
            if not a and prob.get('options') and prob.get('correct') is not None:
                try:
                    a = prob['options'][prob['correct']]
                except (IndexError, TypeError):
                    a = ''
            if q and a:
                cards.append({
                    'front': q,
                    'back': str(a),
                    'hint': prob.get('hint', '')
                })

    # Deduplicate and limit
    seen = set()
    unique = []
    for c in cards:
        key = c['front'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)

    random.shuffle(unique)
    return unique[:count]


def _fallback_quiz(subject, grade, topic, count):
    """Generate quiz questions from curriculum practice problems."""
    data = _load_curriculum(subject, grade)
    lessons = _find_matching_lessons(data, topic)
    questions = []

    for lesson in lessons:
        for prob in lesson.get('practice_problems', []):
            q = {
                'type': prob.get('type', 'fill_in'),
                'question': prob.get('question', ''),
                'hint': prob.get('hint', '')
            }
            if prob.get('type') == 'multiple_choice' and prob.get('options'):
                q['options'] = prob['options']
                q['correct'] = prob.get('correct', 0)
            else:
                q['answer'] = str(prob.get('answer', ''))
            questions.append(q)

    random.shuffle(questions)
    return questions[:count]


def _fallback_practice(subject, grade, topic, count):
    """Generate practice problems from curriculum."""
    data = _load_curriculum(subject, grade)
    lessons = _find_matching_lessons(data, topic)
    problems = []

    for lesson in lessons:
        for prob in lesson.get('practice_problems', []):
            p = {
                'type': prob.get('type', 'fill_in'),
                'question': prob.get('question', ''),
                'hint': prob.get('hint', ''),
                'answer': str(prob.get('answer', ''))
            }
            if prob.get('type') == 'multiple_choice' and prob.get('options'):
                p['options'] = prob['options']
                p['correct'] = prob.get('correct', 0)
            problems.append(p)

    random.shuffle(problems)
    return problems[:count]


def _is_ollama_error(response):
    """Check if the Ollama response is an error message."""
    if not response:
        return True
    return 'trouble thinking' in response.lower() or 'error:' in response.lower()


# ---------------------------------------------------------------------------
# Generation endpoints
# ---------------------------------------------------------------------------

@generate_bp.route('/lesson', methods=['POST'])
def generate_lesson():
    """Generate a structured lesson using AI (with curriculum fallback)."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    subject = data.get('subject', 'math')
    grade = data.get('grade', 3)
    topic = data.get('topic', '')

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    db = get_db()

    # Check cache
    ck = make_cache_key('lesson', subject, grade, topic)
    cached = get_cached_response(db, ck)
    if cached:
        return jsonify({'content': json.loads(cached), 'cached': True})

    # Try LLM first
    system = load_prompt('content_generator.txt', subject=subject, grade=grade, topic=topic)
    messages = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': f'Create a detailed lesson about "{topic}" for grade {grade} {subject}. Return valid JSON with keys: title, explanation, examples (array of {{problem, answer, explanation}}), key_vocabulary (array of strings), real_world (string), practice_problems (array of {{type, question, answer, options (if multiple_choice), correct (index if mc), hint}}).'}
    ]

    response = call_ollama(messages, max_tokens=1500, temperature=0.7)
    parsed = parse_json_response(response)

    if not parsed or _is_ollama_error(response):
        # Fallback to curriculum data
        parsed = _fallback_lesson(subject, grade, topic)

    if subject == 'math' and 'practice_problems' in parsed:
        parsed['practice_problems'] = _validate_math_problems(parsed['practice_problems'])

    content_str = json.dumps(parsed)
    cache_response(db, ck, content_str)
    db.execute(
        'INSERT INTO generated_content (user_id, content_type, subject, grade, topic, content_json) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, 'lesson', subject, grade, topic, content_str)
    )
    db.commit()

    return jsonify({'content': parsed})


@generate_bp.route('/quiz', methods=['POST'])
def generate_quiz():
    """Generate quiz questions using AI (with curriculum fallback)."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    subject = data.get('subject', 'math')
    grade = data.get('grade', 3)
    topic = data.get('topic', '')
    count = min(data.get('count', 5), 15)

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    db = get_db()
    ck = make_cache_key('quiz', subject, grade, topic, count)
    cached = get_cached_response(db, ck)
    if cached:
        return jsonify({'questions': json.loads(cached), 'cached': True})

    system = f"You are a quiz generator for grade {grade} {subject}. Generate exactly {count} quiz questions about {topic}."
    messages = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': f'Generate {count} quiz questions about "{topic}". Return a JSON array where each item has: type ("multiple_choice" or "fill_in"), question (string), options (array of 4 strings, only for multiple_choice), correct (index 0-3 for mc), answer (string for fill_in), hint (string). Make them appropriate for grade {grade}.'}
    ]

    response = call_ollama(messages, max_tokens=1500, temperature=0.8)
    parsed = parse_json_response(response)

    if not parsed or not isinstance(parsed, list) or _is_ollama_error(response):
        parsed = _fallback_quiz(subject, grade, topic, count)

    if not parsed:
        return jsonify({'questions': [], 'error': 'No matching content found for this topic.'}), 200

    if subject == 'math':
        parsed = _validate_math_problems(parsed)

    content_str = json.dumps(parsed)
    cache_response(db, ck, content_str)
    db.execute(
        'INSERT INTO generated_content (user_id, content_type, subject, grade, topic, content_json) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, 'quiz', subject, grade, topic, content_str)
    )
    db.commit()

    return jsonify({'questions': parsed})


@generate_bp.route('/flashcards', methods=['POST'])
def generate_flashcards():
    """Generate flashcards using AI (with curriculum fallback)."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    subject = data.get('subject', 'math')
    grade = data.get('grade', 3)
    topic = data.get('topic', '')
    count = min(data.get('count', 8), 20)

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    db = get_db()
    ck = make_cache_key('flashcards', subject, grade, topic, count)
    cached = get_cached_response(db, ck)
    if cached:
        return jsonify({'flashcards': json.loads(cached), 'cached': True})

    system = load_prompt('flashcard_generator.txt', subject=subject, grade=grade, topic=topic, count=count)
    messages = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': f'Generate {count} flashcards about "{topic}" for grade {grade} {subject}. Return a JSON array of objects with: front (question/term), back (answer/definition), hint (optional helper text).'}
    ]

    response = call_ollama(messages, max_tokens=1000, temperature=0.7)
    parsed = parse_json_response(response)

    if not parsed or not isinstance(parsed, list) or _is_ollama_error(response):
        parsed = _fallback_flashcards(subject, grade, topic, count)

    if not parsed:
        return jsonify({'flashcards': [], 'error': 'No matching content found for this topic.'}), 200

    content_str = json.dumps(parsed)
    cache_response(db, ck, content_str)

    # Save individual flashcards to the flashcards table
    for card in parsed:
        db.execute(
            'INSERT INTO flashcards (user_id, subject, grade, topic, front, back, hint, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, subject, grade, topic, card.get('front', ''), card.get('back', ''), card.get('hint', ''), 'ai')
        )

    db.execute(
        'INSERT INTO generated_content (user_id, content_type, subject, grade, topic, content_json) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, 'flashcards', subject, grade, topic, content_str)
    )
    db.commit()

    return jsonify({'flashcards': parsed})


@generate_bp.route('/practice', methods=['POST'])
def generate_practice():
    """Generate practice problems using AI (with curriculum fallback)."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    subject = data.get('subject', 'math')
    grade = data.get('grade', 3)
    topic = data.get('topic', '')
    count = min(data.get('count', 5), 15)
    types = data.get('types', ['multiple_choice', 'fill_in'])

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    db = get_db()

    type_str = ', '.join(types)
    system = f"You are a practice problem generator for grade {grade} {subject}."
    messages = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': f'Generate {count} practice problems about "{topic}" using these types: {type_str}. Return a JSON array where each item has: type, question, answer, options (for mc), correct (index for mc), hint. Grade level: {grade}.'}
    ]

    response = call_ollama(messages, max_tokens=1200, temperature=0.8)
    parsed = parse_json_response(response)

    if not parsed or not isinstance(parsed, list) or _is_ollama_error(response):
        parsed = _fallback_practice(subject, grade, topic, count)

    if not parsed:
        return jsonify({'problems': [], 'error': 'No matching content found for this topic.'}), 200

    if subject == 'math':
        parsed = _validate_math_problems(parsed)

    content_str = json.dumps(parsed)
    db.execute(
        'INSERT INTO generated_content (user_id, content_type, subject, grade, topic, content_json) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, 'practice', subject, grade, topic, content_str)
    )
    db.commit()

    return jsonify({'problems': parsed})


@generate_bp.route('/saved', methods=['GET'])
def get_saved_content():
    """Get user's saved AI-generated content."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    rows = db.execute(
        'SELECT id, content_type, subject, grade, topic, created_at FROM generated_content WHERE user_id = ? ORDER BY created_at DESC LIMIT 50',
        (user_id,)
    ).fetchall()

    return jsonify({'items': [dict(r) for r in rows]})


@generate_bp.route('/saved/<int:item_id>', methods=['GET'])
def get_saved_item(item_id):
    """Get a specific saved content item."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    row = db.execute(
        'SELECT * FROM generated_content WHERE id = ? AND user_id = ?',
        (item_id, user_id)
    ).fetchone()

    if not row:
        return jsonify({'error': 'Not found'}), 404

    result = dict(row)
    result['content'] = json.loads(result['content_json'])
    del result['content_json']
    return jsonify(result)


@generate_bp.route('/saved/<int:item_id>', methods=['DELETE'])
def delete_saved_item(item_id):
    """Delete a saved content item."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    db.execute('DELETE FROM generated_content WHERE id = ? AND user_id = ?', (item_id, user_id))
    db.commit()
    return jsonify({'message': 'Deleted'})


def _validate_math_problems(problems):
    """Validate math problem answers using Python computation."""
    try:
        from fractions import Fraction
        for prob in problems:
            answer = prob.get('answer')
            if answer and isinstance(answer, str):
                try:
                    val = eval(answer.replace('x', '*').replace('^', '**'),
                             {"__builtins__": {}},
                             {"Fraction": Fraction, "abs": abs, "round": round})
                    prob['_validated'] = True
                except Exception:
                    pass
    except Exception:
        pass
    return problems
