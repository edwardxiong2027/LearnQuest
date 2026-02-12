# LearnQuest

**Learn Without Limits — Free Education for All**

A complete, self-contained, offline K-12 tutoring platform that runs from a USB drive. Powered by a local AI tutor — no internet required, no data collected, no cost to students.

Created by **Diamond Bar High School Vibe Coding Club**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Website](https://img.shields.io/badge/Website-learnquest2026.web.app-purple)](https://learnquest2026.web.app)

---

## What is LearnQuest?

LearnQuest is like Khan Academy on a USB stick — but without video and with a private AI tutor. Plug it into any computer, launch it, and start learning. Everything runs locally: the AI model, the curriculum, the database, the web app. Your data never leaves the machine.

**4 subjects. 13 grade levels. 500+ lessons. Zero internet.**

| Subject | Grades | Topics |
|---------|--------|--------|
| Math | K-12 | Counting through Pre-Calculus |
| Science | K-12 | Five Senses through Earth & Environmental Science |
| ELA | K-12 | Phonics through College Prep Writing |
| Social Studies | K-12 | Community Helpers through Government & Economics |

---

## Features

### Learning
- **Comprehensive Curriculum** — 6-10 units per subject per grade, each with 4-6 lessons and practice problems
- **AI Tutor** — Chat with a friendly Learning Buddy that uses the Socratic method (never gives away answers)
- **AI Studio** — Generate custom lessons, quizzes, flashcards, and worksheets on any topic
- **Math Accuracy** — All math is computed by Python (fractions, algebra, trigonometry, calculus). The AI only explains — it never computes.

### Study Tools
- **Flashcards** with Leitner spaced repetition
- **Vocabulary Builder** that collects key terms from completed lessons
- **Study Timer** (Pomodoro style with XP rewards)
- **Notes & Bookmarks** on any lesson
- **Printable Worksheets** with answer keys
- **Cross-lesson Search**

### Gamification
- **XP & Levels** — 50 levels from "Number Newbie" to "LearnQuest Legend"
- **30+ Badges** — mastery, streaks, speed, exploration
- **Daily Streaks** with flame animations
- **Daily Challenge** for bonus XP
- **Leaderboard** (optional, teacher-controlled)

### Teacher Dashboard
- Add/edit/delete students (name + PIN, no email needed)
- Per-student progress reports and analytics
- Classroom mode: share a network URL so the whole class connects via WiFi
- CSV export for grade books
- Toggle gamification, leaderboard, and timer settings

---

## System Requirements

| | Minimum | Recommended |
|---|---------|-------------|
| **OS** | macOS 10.15+, Windows 10+, Linux, ChromeOS | macOS 12+ or Windows 11 |
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 4 GB | 8 GB+ |
| **Disk** | ~3 GB (with smallest model) | ~5 GB (with default model) |
| **Browser** | Any modern browser | Chrome, Firefox, Safari, Edge |

---

## Quick Start

### 1. First-Time Setup

The interactive setup wizard detects your OS, checks dependencies, and lets you choose an AI model:

```bash
python launch.py wizard
```

The wizard will:
1. Detect your operating system
2. Check that Python and Ollama are installed (with install instructions if not)
3. Let you pick an AI model based on your hardware
4. Create a virtual environment and install dependencies
5. Download the AI model to the USB
6. Initialize the database

**Model options:**

| Model | Size | RAM | Best For |
|-------|------|-----|----------|
| Phi-3 Mini (default) | ~2.3 GB | 8 GB+ | K-12, best quality/size balance |
| Llama 3.2 1B | ~1.3 GB | 4 GB+ | K-5, low-spec machines |
| Llama 3.2 3B | ~2.0 GB | 8 GB+ | K-8, good alternative |
| Phi-3 Medium | ~7.9 GB | 16 GB+ | K-12, highest quality |

### 2. Start Learning

```bash
python launch.py start
```

Opens automatically at **http://localhost:5001**

### 3. Stop

```bash
python launch.py stop
```

### Platform-Specific Alternatives

**Mac / Linux (shell scripts):**
```bash
chmod +x setup.sh start.sh stop.sh
./setup.sh    # first time
./start.sh    # start
./stop.sh     # stop
```

**Windows (batch files):**
```batch
setup.bat     :: first time
start.bat     :: start
stop.bat      :: stop
```

---

## Default Accounts

| Name | PIN | Role |
|------|-----|------|
| teacher | 1234 | Teacher |

Teachers create student accounts from the Dashboard. Students only need a name and a 4-digit PIN.

---

## Deployment Modes

### Personal Mode (default)
One student per USB. Plug into any computer and start learning. Progress is saved on the USB.

### Classroom Mode
A teacher starts LearnQuest on one computer. Students connect from their own devices over WiFi:
1. Teacher logs in → Dashboard → Classroom Setup
2. Share the network URL or QR code with students
3. Students open the URL in their browser and log in

---

## Architecture

```
LearnQuest/
├── launch.py              # Cross-platform launcher (setup, start, stop, wizard)
├── setup.sh / start.sh    # Mac/Linux shell scripts
├── setup.bat / start.bat  # Windows batch scripts
├── config.json            # Local settings (model, port) — created by wizard
├── ollama_models/         # AI model storage (downloaded on setup)
├── website/               # Firebase showcase site (learnquest2026.web.app)
└── app/
    ├── server.py           # Flask backend (port 5001)
    ├── database/
    │   ├── schema.sql      # SQLite schema
    │   └── learnquest.db   # Database (generated on setup)
    ├── api/                # REST API routes
    │   ├── routes_auth.py       # Login / registration
    │   ├── routes_lessons.py    # Curriculum & lessons
    │   ├── routes_tutor.py      # AI tutor chat (SSE streaming)
    │   ├── routes_quiz.py       # Quizzes & daily challenges
    │   ├── routes_progress.py   # XP, badges, streaks
    │   ├── routes_teacher.py    # Teacher dashboard
    │   ├── routes_search.py     # Content search
    │   └── llm_utils.py         # Ollama integration
    ├── math_engine/        # Deterministic math (never uses AI)
    │   ├── arithmetic.py        # +, -, ×, ÷
    │   ├── fractions_ops.py     # Fraction operations
    │   ├── algebra.py           # Linear equations
    │   ├── advanced_algebra.py  # Quadratics, systems, polynomials, complex numbers
    │   ├── geometry.py          # Area, perimeter, volume, circles, 3D
    │   ├── statistics.py        # Mean, median, mode, std dev, probability
    │   ├── trigonometry.py      # Unit circle, SOH-CAH-TOA, law of sines/cosines
    │   ├── precalculus.py       # Logarithms, exponentials, limits, matrices, vectors
    │   ├── problem_generator.py # Grade-appropriate problem generation
    │   ├── step_solver.py       # Step-by-step solutions
    │   └── answer_validator.py  # Validates equivalent answer forms
    ├── content/            # Curriculum JSON (K-12, all 4 subjects)
    │   ├── curriculum_map.json
    │   ├── math/           # k.json through 12.json
    │   ├── science/        # k.json through 12.json
    │   ├── ela/            # k.json through 12.json
    │   └── social_studies/ # k.json through 12.json
    ├── prompts/            # LLM system prompts (tutor, quiz, hints, etc.)
    ├── static/
    │   ├── css/styles.css  # Full styling (dark mode, responsive)
    │   ├── js/             # Vanilla JS SPA
    │   │   ├── app.js           # Router & state management
    │   │   ├── tutor.js         # AI chat interface
    │   │   ├── lessons.js       # Lesson viewer
    │   │   ├── quiz.js          # Quiz engine
    │   │   ├── progress.js      # Progress tracking
    │   │   ├── gamification.js  # Badges, streaks, leaderboard
    │   │   └── generate.js      # AI Studio (content generation)
    │   ├── images/         # SVG icons, badges, avatars
    │   └── sounds/         # Achievement sounds
    └── templates/
        └── index.html      # SPA shell
```

### Tech Stack
- **Backend**: Python 3 + Flask + SQLite
- **Frontend**: Vanilla JavaScript SPA (no frameworks, no build step)
- **AI**: Ollama (configurable model — Phi-3 Mini default)
- **Math**: Python `fractions` + `sympy` (deterministic, never AI-computed)
- **Hosting**: Firebase (showcase website only — the app itself is fully offline)

### Key Design Decisions
- **Math accuracy over speed**: Every math answer is computed by Python. The LLM only generates explanations and encouragement.
- **No external dependencies at runtime**: All CSS, JS, fonts, and icons are local. No CDNs.
- **Portable**: The entire app lives on the USB. Nothing installs to the host except Ollama.
- **Privacy**: No accounts, no telemetry, no data collection. Everything stays on the USB.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Run `python launch.py setup` again |
| AI tutor not responding | Check Ollama is running: `ollama list` |
| Slow responses | Normal — local AI takes 10-20 sec on first response |
| Port 5001 in use | `LEARNQUEST_PORT=5002 python launch.py start` |
| Python not found | Install from [python.org](https://python.org) and add to PATH |
| Ollama not found | Install from [ollama.com](https://ollama.com) |
| Chromebook | Requires Linux (Crostini) enabled in settings |

---

## Contributing

Contributions are welcome! This is an open-source project by high school students.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test locally: `python launch.py start`
5. Submit a pull request

**Areas where we'd love help:**
- Additional curriculum content (especially for grades 9-12 electives)
- Accessibility improvements
- Translations / multilingual support
- Performance optimizations for low-spec Chromebooks
- Additional math engine coverage

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Credits

Built by the **Diamond Bar High School Vibe Coding Club** (Diamond Bar, CA).

Our mission: make quality education accessible to every student, regardless of internet access or ability to pay.

---

*Learn Without Limits.*
