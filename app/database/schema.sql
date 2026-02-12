-- LearnQuest Database Schema

-- Users (students and teachers)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pin TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    grade INTEGER DEFAULT 3,
    avatar TEXT DEFAULT 'owl',
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_active DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Lesson progress
CREATE TABLE IF NOT EXISTS lesson_progress (
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
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    quiz_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    grade INTEGER NOT NULL,
    score REAL NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    time_spent_seconds INTEGER,
    answers_json TEXT,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Badges earned
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    badge_id TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    badge_description TEXT,
    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- Chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    session_id TEXT NOT NULL,
    lesson_id TEXT,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily challenges
CREATE TABLE IF NOT EXISTS daily_challenges (
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
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- LLM response cache
CREATE TABLE IF NOT EXISTS llm_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    response TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Generated content (AI Studio)
CREATE TABLE IF NOT EXISTS generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    content_type TEXT NOT NULL,
    subject TEXT,
    grade INTEGER,
    topic TEXT,
    content_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    subject TEXT NOT NULL,
    grade INTEGER,
    topic TEXT,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    hint TEXT,
    source TEXT DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Flashcard progress (Leitner boxes)
CREATE TABLE IF NOT EXISTS flashcard_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    flashcard_id INTEGER REFERENCES flashcards(id),
    box INTEGER DEFAULT 1,
    next_review DATE,
    last_reviewed DATETIME,
    times_correct INTEGER DEFAULT 0,
    times_wrong INTEGER DEFAULT 0,
    UNIQUE(user_id, flashcard_id)
);

-- Notes
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    lesson_id TEXT,
    lesson_title TEXT,
    subject TEXT,
    grade INTEGER,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bookmarks
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    lesson_id TEXT NOT NULL,
    lesson_title TEXT,
    subject TEXT,
    grade INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, lesson_id)
);

-- Tutor conversations
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    session_id TEXT NOT NULL,
    title TEXT DEFAULT 'New Conversation',
    subject TEXT,
    pinned BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, session_id)
);

-- Default teacher account (pin: 1234)
INSERT OR IGNORE INTO users (name, pin, role, grade) VALUES ('teacher', '1234', 'teacher', 0);

-- Default settings
INSERT OR IGNORE INTO settings (key, value) VALUES ('leaderboard_enabled', 'true');
INSERT OR IGNORE INTO settings (key, value) VALUES ('quiz_timer_enabled', 'false');
INSERT OR IGNORE INTO settings (key, value) VALUES ('quiz_timer_seconds', '300');
INSERT OR IGNORE INTO settings (key, value) VALUES ('gamification_enabled', 'true');
INSERT OR IGNORE INTO settings (key, value) VALUES ('deployment_mode', 'personal');
