# Claude Code Prompt: Build K-8 Offline Tutoring Platform on USB

## MISSION

Build a complete, self-contained, offline K-8 tutoring platform (similar to Khan Academy but without video) on my USB drive at `/Volumes/LLM_USB`. This platform must be fully portable — I can plug the USB into any Mac and run it with one command. No internet required after initial setup.

## TECH STACK

- **LLM**: Phi-3 Mini via Ollama (download the model to the USB)
- **Backend**: Python 3 + Flask (use a portable Python bundled on the USB)
- **Frontend**: Single-page app using HTML/CSS/JavaScript (no npm/node needed)
- **Database**: SQLite (stored on USB)
- **Everything lives on the USB. Nothing installs to the host machine except Ollama if not already present.**

## USB STRUCTURE

```
/Volumes/LLM_USB/
├── start.sh                    # One-click launcher script
├── stop.sh                     # Graceful shutdown
├── setup.sh                    # First-time setup (installs Ollama if needed, pulls phi3)
├── README.md                   # Instructions for teachers
├── ollama_models/              # Ollama model storage
├── app/
│   ├── server.py               # Flask backend
│   ├── requirements.txt        # Python dependencies
│   ├── venv/                   # Python virtual environment
│   ├── database/
│   │   ├── schema.sql
│   │   └── learnquest.db       # SQLite database
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css      # Full styling - modern, colorful, kid-friendly
│   │   ├── js/
│   │   │   ├── app.js          # Main SPA router & state management
│   │   │   ├── tutor.js        # LLM chat/tutoring interface
│   │   │   ├── lessons.js      # Lesson viewer
│   │   │   ├── quiz.js         # Quiz engine
│   │   │   ├── progress.js     # Progress tracking & XP system
│   │   │   └── gamification.js # Badges, streaks, leaderboard
│   │   ├── images/             # Icons, badges, avatars (use SVG/CSS art, no external deps)
│   │   └── sounds/             # Optional: achievement sounds (small mp3s)
│   ├── templates/
│   │   └── index.html          # Main SPA shell
│   ├── content/
│   │   ├── math/
│   │   │   ├── k.json          # Kindergarten
│   │   │   ├── 1.json          # Grade 1
│   │   │   ├── 2.json          # Grade 2
│   │   │   ├── 3.json          # Grade 3
│   │   │   ├── 4.json          # Grade 4
│   │   │   ├── 5.json          # Grade 5
│   │   │   ├── 6.json          # Grade 6
│   │   │   ├── 7.json          # Grade 7
│   │   │   └── 8.json          # Grade 8
│   │   ├── science/
│   │   │   ├── k.json through 8.json
│   │   ├── ela/                # English Language Arts
│   │   │   ├── k.json through 8.json
│   │   ├── social_studies/
│   │   │   ├── k.json through 8.json
│   │   └── curriculum_map.json # Master curriculum tree
│   ├── prompts/
│   │   ├── tutor_math.txt      # System prompt for math tutoring
│   │   ├── tutor_science.txt   # System prompt for science tutoring
│   │   ├── tutor_ela.txt       # System prompt for ELA tutoring
│   │   ├── tutor_social.txt    # System prompt for social studies
│   │   ├── quiz_generator.txt  # System prompt for generating quizzes
│   │   └── hint_generator.txt  # System prompt for generating hints
│   └── api/
│       ├── __init__.py
│       ├── routes_auth.py      # Student/teacher login
│       ├── routes_lessons.py   # Lesson content serving
│       ├── routes_tutor.py     # LLM tutoring endpoints
│       ├── routes_quiz.py      # Quiz endpoints
│       ├── routes_progress.py  # Progress & gamification
│       └── routes_teacher.py   # Teacher dashboard
```

## CRITICAL REQUIREMENTS

### 1. MATH ACCURACY
This is the most important requirement. Small LLMs make math errors. Implement these safeguards:
- **Built-in Python math validator**: For arithmetic, fractions, algebra — compute the correct answer in Python FIRST, then use the LLM only for EXPLANATION. Never trust the LLM to compute.
- **Math problem engine**: Generate problems programmatically with known correct answers. The LLM explains, Python validates.
- **Answer checking**: Always verify student answers with Python computation, not LLM judgment.
- **Step-by-step solver**: For showing work, use a deterministic solver (sympy or custom) and have the LLM narrate the steps in kid-friendly language.

Example flow:
```
Student sees: "What is 3/4 + 1/2?"
Python computes: answer = Fraction(3,4) + Fraction(1,2) = Fraction(5,4) = "1 1/4"
Student answers: "4/6"
Python checks: WRONG
LLM generates: "Good try! Let's look at this together. When we add fractions, we need a common denominator first..."
```

### 2. CURRICULUM CONTENT (Pre-built, comprehensive)
Build REAL, detailed curriculum content for every grade K-8. Each grade JSON should contain:

```json
{
  "grade": 3,
  "subject": "math",
  "units": [
    {
      "id": "3-math-1",
      "title": "Multiplication & Division",
      "description": "Understanding multiplication as groups of objects",
      "lessons": [
        {
          "id": "3-math-1-1",
          "title": "What is Multiplication?",
          "type": "lesson",
          "content": {
            "explanation": "Multiplication is a quick way to add equal groups...",
            "examples": [
              {"problem": "3 × 4", "visual": "3 groups of 4 dots", "answer": "12", "explanation": "3 groups of 4 is the same as 4 + 4 + 4 = 12"}
            ],
            "key_vocabulary": ["multiply", "factors", "product", "groups"],
            "real_world": "If you have 3 bags with 4 apples each, how many apples total?"
          },
          "practice_problems": [
            {"type": "multiple_choice", "question": "What is 2 × 5?", "options": ["7", "10", "25", "3"], "correct": 1, "hint": "Think of 2 groups of 5"},
            {"type": "fill_in", "question": "4 × 3 = ___", "answer": "12", "hint": "Count 4 groups of 3"},
            {"type": "word_problem", "question": "Sam has 5 boxes. Each box has 6 crayons. How many crayons does Sam have?", "answer": "30", "operation": "5 * 6"}
          ],
          "xp_reward": 20
        }
      ],
      "unit_quiz": {
        "questions": [...],
        "passing_score": 70,
        "xp_reward": 50,
        "badge": "multiplication_master"
      }
    }
  ]
}
```

**MATH CURRICULUM MAP (aligned to Common Core):**

**Kindergarten**: Counting to 100, number recognition, basic addition/subtraction within 10, shapes, comparing sizes
**Grade 1**: Addition/subtraction within 20, place value (tens/ones), measuring lengths, telling time, basic shapes & fractions (halves/quarters)
**Grade 2**: Addition/subtraction within 100, intro to multiplication concept, measuring in standard units, money, bar graphs, basic geometry
**Grade 3**: Multiplication & division within 100, fractions (number line, comparing), area & perimeter, time elapsed, bar/picture graphs
**Grade 4**: Multi-digit multiplication, long division, fraction equivalence & operations, decimals intro, angles, line plots
**Grade 5**: Fraction operations (add/subtract/multiply), decimals operations, volume, coordinate plane, order of operations
**Grade 6**: Ratios & proportions, dividing fractions, integers & rational numbers, expressions & equations, area/surface area/volume, statistics
**Grade 7**: Proportional relationships, operations with rational numbers, expressions & equations, geometry (scale, circles, angles), probability & statistics
**Grade 8**: Linear equations, functions, Pythagorean theorem, transformations, scatter plots, exponents, intro to irrational numbers

**SCIENCE CURRICULUM MAP:**
**K-2**: Five senses, animals & habitats, weather & seasons, plants, states of matter, push/pull forces
**3-5**: Ecosystems, life cycles, rock cycle, water cycle, solar system, energy & electricity, simple machines
**6-8**: Cells & body systems, genetics basics, chemistry (atoms, periodic table, reactions), physics (motion, forces, energy), earth science (plate tectonics, climate), scientific method

**ELA CURRICULUM MAP:**
**K-2**: Phonics, sight words, reading comprehension (fiction/nonfiction), sentence structure, capitalization & punctuation, narrative writing
**3-5**: Reading comprehension strategies, paragraph writing, grammar (parts of speech, subject-verb agreement), persuasive writing, research basics, poetry
**6-8**: Literary analysis, essay writing (argumentative, expository, narrative), grammar & mechanics, vocabulary building, research papers, rhetoric

**SOCIAL STUDIES CURRICULUM MAP:**
**K-2**: Community helpers, maps & globes, US symbols & holidays, basic citizenship, families & cultures
**3-5**: Native Americans, colonial America, American Revolution, US geography, state government, economics basics
**6-8**: Ancient civilizations, world geography, US history (Civil War through modern), civics & government, world cultures, economics

**EACH GRADE MUST HAVE AT LEAST 6-8 UNITS PER SUBJECT, EACH UNIT WITH 4-6 LESSONS, EACH LESSON WITH 5-10 PRACTICE PROBLEMS.** This is a LOT of content — generate it all. Do not leave placeholders.

### 3. GAMIFICATION SYSTEM
Make it fun and addictive for kids:

- **XP Points**: Earn XP for completing lessons (20 XP), quizzes (50 XP), perfect scores (bonus 25 XP), daily login (10 XP)
- **Levels**: Level 1 (0 XP) through Level 50 (25,000 XP) with creative names ("Number Newbie", "Fraction Fighter", "Algebra Ace", etc.)
- **Badges**: Unlock badges for achievements:
  - Subject mastery badges (complete all units in a subject for a grade)
  - Streak badges (3-day, 7-day, 30-day streaks)
  - Perfect score badges
  - Speed badges (complete quiz under time)
  - Helper badges (use the tutor chat feature)
  - Explorer badges (try all 4 subjects)
- **Daily Streaks**: Track consecutive days of learning. Visual flame icon that grows.
- **Leaderboard**: Class leaderboard (optional, teacher can enable/disable)
- **Avatar System**: Students pick/customize a simple avatar. Unlock new avatar items with XP.
- **Progress Map**: Visual map for each subject showing completed/locked lessons (like a game world map)
- **Achievement Animations**: CSS animations when earning badges/leveling up. Confetti, glow effects, etc.
- **Energy System**: NOT a limiting system — just a visual "brain energy" bar that fills as they learn

### 4. STUDENT EXPERIENCE

**Home Screen**: 
- Welcome message with student name and avatar
- Daily streak counter with flame animation
- "Continue Learning" button (picks up where they left off)
- XP bar showing progress to next level
- Subject cards (Math, Science, ELA, Social Studies) with progress rings
- Recent badges earned
- Daily challenge (one random problem for bonus XP)

**Lesson Flow**:
1. Student picks subject → sees grade-level units on a visual map
2. Clicks a lesson → reads explanation with examples
3. Interactive practice problems with immediate feedback
4. "I don't understand" button → opens AI tutor chat for that specific topic
5. Complete all problems → earn XP → unlock next lesson
6. Unit quiz after completing all lessons in a unit → badge on pass

**AI Tutor Chat**:
- Persistent chat panel (slide-in from right side)
- Context-aware: knows what lesson/topic the student is on
- Socratic method: guides with questions, doesn't just give answers
- Adjusts language to grade level
- Uses encouraging, warm tone
- Can generate additional practice problems on request
- "Explain it differently" button for alternative explanations

**Quiz System**:
- Multiple question types: multiple choice, fill-in, true/false, matching, word problems
- Timer (optional, teacher can set)
- Immediate feedback per question with explanation
- Score summary at end with breakdown
- Retry option (different questions generated)
- Adaptive: if student fails, suggest reviewing specific lessons

### 5. TEACHER DASHBOARD

- **Class Management**: Add students (just name + simple PIN, no emails needed)
- **Progress Overview**: See all students' progress at a glance — grid of students × subjects with color-coded status
- **Individual Reports**: Click a student to see detailed progress, time spent, quiz scores, struggle areas
- **Content Management**: Enable/disable subjects or units. Assign specific lessons or quizzes.
- **Quiz Builder**: Create custom quizzes from the question bank or let AI generate them
- **Settings**: Toggle leaderboard, set quiz timers, adjust difficulty, manage gamification settings
- **Export**: Export progress reports as CSV

### 6. UI/UX DESIGN

- **Modern, colorful, kid-friendly** but not babyish (works for K-8)
- **Color scheme**: Vibrant but not overwhelming. Use a primary blue (#4A90D9), accent green (#2ECC71), warm orange (#F39C12), and purple (#9B59B6) for different subjects
- **Typography**: Clean sans-serif (system fonts — no external font loading)
- **Responsive**: Works on laptops, tablets, Chromebooks
- **Accessible**: Good contrast ratios, keyboard navigable, screen reader friendly
- **Dark mode toggle**
- **Animations**: Subtle, delightful micro-animations. Confetti on achievements. Smooth transitions.
- **No external dependencies**: All CSS/JS is local. No CDNs. No Google Fonts. Everything offline.
- **Loading states**: Show a friendly loading animation while LLM generates responses
- **Mascot**: A friendly owl character (CSS/SVG) that appears in the UI with encouraging messages

### 7. SETUP & PORTABILITY

**setup.sh** should:
1. Check if Ollama is installed. If not, download and install it.
2. Set OLLAMA_MODELS environment variable to point to USB's ollama_models/ directory
3. Pull phi3 model (stored on USB)
4. Create Python virtual environment on the USB
5. Install Flask and dependencies into the venv
6. Initialize the SQLite database
7. Print success message with instructions

**start.sh** should:
1. Set OLLAMA_MODELS to USB path
2. Start Ollama serve in background
3. Activate venv
4. Start Flask server
5. Open browser to http://localhost:5000
6. Print "LearnQuest is running! Open http://localhost:5000"

**stop.sh** should:
1. Kill Flask server
2. Kill Ollama serve
3. Print "LearnQuest stopped. Safe to remove USB."

**IMPORTANT**: The scripts must detect the USB mount path dynamically (it might not always be /Volumes/LLM_USB). Use the script's own directory as the base path.

### 8. API ENDPOINTS

```
POST /api/auth/login          # Student/teacher login (name + PIN)
POST /api/auth/register       # Register new student (teacher creates)
GET  /api/curriculum           # Get curriculum map
GET  /api/curriculum/:subject/:grade  # Get all units for a subject+grade
GET  /api/lesson/:id          # Get lesson content
POST /api/lesson/:id/complete  # Mark lesson complete, award XP
GET  /api/quiz/:unitId        # Get quiz for a unit
POST /api/quiz/submit         # Submit quiz answers, get results
POST /api/quiz/generate       # AI-generate a quiz for a topic
POST /api/tutor/chat          # Send message to AI tutor
POST /api/tutor/hint          # Get hint for a specific problem
POST /api/math/check          # Validate a math answer (Python computation)
POST /api/math/solve          # Get step-by-step solution
GET  /api/progress/:studentId  # Get student progress
GET  /api/progress/badges      # Get all available and earned badges
GET  /api/leaderboard         # Get class leaderboard
GET  /api/daily-challenge     # Get today's challenge problem
POST /api/daily-challenge/submit  # Submit daily challenge answer
GET  /api/teacher/students    # List all students
GET  /api/teacher/report/:studentId  # Detailed student report
POST /api/teacher/export      # Export progress as CSV
GET  /api/teacher/settings    # Get platform settings
POST /api/teacher/settings    # Update settings
```

### 9. DATABASE SCHEMA

```sql
-- Users (students and teachers)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pin TEXT NOT NULL,
    role TEXT DEFAULT 'student', -- 'student' or 'teacher'
    grade INTEGER DEFAULT 3,
    avatar TEXT DEFAULT 'owl',
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_active DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Lesson progress
CREATE TABLE lesson_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    lesson_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    grade INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    score REAL,
    time_spent_seconds INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    completed_at DATETIME,
    UNIQUE(user_id, lesson_id)
);

-- Quiz results
CREATE TABLE quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    quiz_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    grade INTEGER NOT NULL,
    score REAL NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    time_spent_seconds INTEGER,
    answers_json TEXT, -- JSON blob of individual answers
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Badges earned
CREATE TABLE badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    badge_id TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    badge_description TEXT,
    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- Chat history
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    session_id TEXT NOT NULL,
    lesson_id TEXT,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily challenges
CREATE TABLE daily_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    challenge_date DATE NOT NULL,
    subject TEXT NOT NULL,
    question_json TEXT NOT NULL,
    answer TEXT,
    correct BOOLEAN,
    completed_at DATETIME,
    UNIQUE(user_id, challenge_date)
);

-- Teacher settings
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### 10. LLM SYSTEM PROMPTS

**Math Tutor Prompt** (tutor_math.txt):
```
You are LearnQuest Math Buddy, a friendly and patient math tutor for students in grades K-8. 

RULES:
- NEVER give the answer directly. Guide the student to discover it themselves using the Socratic method.
- Use simple, age-appropriate language. Adjust based on the grade level provided in context.
- Use real-world examples kids can relate to (pizza slices, candy, toys, sports).
- Be enthusiastic and encouraging. Celebrate effort, not just correctness.
- If a student is wrong, say something positive first ("Good thinking!") then guide them.
- Use step-by-step reasoning. Break complex problems into small pieces.
- For younger grades (K-2), use very simple words and short sentences.
- For middle grades (3-5), you can use more math vocabulary but always explain it.
- For upper grades (6-8), use proper math terminology and encourage formal reasoning.
- NEVER do the computation. Say things like "What do you get when you..." or "Try adding those together..."
- If the student is frustrated, acknowledge it: "Math can be tricky sometimes! Let's try a different approach."
- Keep responses under 150 words for K-2, under 200 words for 3-5, under 250 words for 6-8.

CONTEXT: The student is in grade {grade}, working on {topic} in the lesson "{lesson_title}".
```

Create similar detailed prompts for science, ELA, social studies, quiz generation, and hint generation.

### 11. MATH ENGINE

Build a robust Python math engine that handles:
- **Arithmetic**: +, -, ×, ÷ with whole numbers, decimals, fractions
- **Fractions**: Addition, subtraction, multiplication, division, simplification, comparison, mixed numbers
- **Algebra (6-8)**: Solve linear equations, evaluate expressions, simplify
- **Geometry**: Area, perimeter, volume calculations for basic shapes
- **Statistics (6-8)**: Mean, median, mode, range
- **Problem generation**: Programmatically generate problems at appropriate difficulty for each grade/topic
- **Answer validation**: Check student answers with tolerance for equivalent forms (e.g., "1/2" = "2/4" = "0.5")
- **Step-by-step solutions**: Generate the solution steps deterministically, then optionally have LLM narrate them

Use Python's `fractions.Fraction` and `sympy` (include in requirements) for math operations. NEVER rely on the LLM for computation.

### 12. IMPORTANT TECHNICAL NOTES

- Use `OLLAMA_MODELS` env var to store models on USB, not in ~/.ollama
- Flask should bind to `0.0.0.0:5000` so other devices on the same WiFi can also access it
- All API calls to Ollama use `http://localhost:11434/api/generate` or `/api/chat`
- Stream LLM responses to the frontend using Server-Sent Events for a nice typing effect
- Implement request queuing — if multiple students ask the LLM at once, queue and process sequentially
- Cache common LLM responses (same topic + grade explanations) in SQLite to reduce LLM calls
- All dates/times should work offline (use system clock)
- Default teacher account: name="teacher", pin="1234" (prompt to change on first login)
- The app name is **"LearnQuest"**

## EXECUTION INSTRUCTIONS

1. Build everything on the USB at /Volumes/LLM_USB
2. Generate ALL curriculum content — do not use placeholders. Every grade, every subject, every unit, every lesson, every practice problem.
3. Test that setup.sh, start.sh, and stop.sh all work
4. Test the math engine thoroughly — accuracy is critical
5. Make the UI polished and delightful — this is for kids, it needs to feel fun
6. After building, run the app and verify the core flow: login → pick subject → lesson → practice → quiz → earn XP/badge

**This should be a production-quality application, not a prototype.** Take your time and build it right.
