/**
 * LearnQuest - Main SPA Router & State Management
 */

const App = {
    state: {
        user: null,
        currentPage: 'login',
        darkMode: localStorage.getItem('darkMode') === 'true',
        curriculum: null,
    },

    /** Initialize the application */
    init() {
        if (this.state.darkMode) {
            document.body.classList.add('dark-mode');
        }
        // Check for existing session
        this.checkSession();
    },

    /** API helper */
    async api(endpoint, options = {}) {
        const config = {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        };
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }
        try {
            const resp = await fetch(endpoint, config);
            const data = await resp.json();
            if (!resp.ok) {
                throw new Error(data.error || `HTTP ${resp.status}`);
            }
            return data;
        } catch (err) {
            if (err.message && !err.message.startsWith('HTTP')) {
                console.error('API Error:', err);
            }
            throw err;
        }
    },

    /** Check if user has active session */
    async checkSession() {
        try {
            const data = await this.api('/api/auth/session');
            if (data.user) {
                this.state.user = data.user;
                this.onLoginSuccess();
                return;
            }
        } catch (e) {
            // No session
        }
        this.navigate('login');
    },

    /** Handle successful login */
    onLoginSuccess() {
        const nav = document.getElementById('main-nav');
        nav.classList.remove('hidden');

        const footer = document.getElementById('app-footer');
        if (footer) footer.classList.remove('hidden');

        // Show/hide teacher nav
        const teacherBtns = document.querySelectorAll('.teacher-only');
        teacherBtns.forEach(btn => {
            btn.style.display = this.state.user.role === 'teacher' ? '' : 'none';
        });

        // Show/hide student nav
        const studentBtns = document.querySelectorAll('.student-only');
        studentBtns.forEach(btn => {
            btn.style.display = this.state.user.role === 'student' ? '' : 'none';
        });

        // Update nav info
        document.getElementById('nav-username').textContent = this.state.user.name;
        document.getElementById('nav-xp-value').textContent = this.state.user.xp || 0;
        document.getElementById('nav-streak-value').textContent = this.state.user.streak_days || 0;

        // Show tutor FAB for students
        const tutorToggle = document.getElementById('tutor-toggle');
        tutorToggle.classList.toggle('hidden', this.state.user.role === 'teacher');

        this.navigate('home');
    },

    /** SPA Router */
    navigate(page, params = {}) {
        this.state.currentPage = page;
        const main = document.getElementById('main-content');

        // Update nav active state
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.page === page);
        });

        // Close user dropdown
        document.getElementById('user-dropdown')?.classList.add('hidden');

        switch (page) {
            case 'login':
                this.renderLogin(main);
                break;
            case 'home':
                this.renderHome(main);
                break;
            case 'subjects':
                this.renderSubjects(main);
                break;
            case 'units':
                Lessons.renderUnits(main, params.subject, params.grade);
                break;
            case 'lesson':
                Lessons.renderLesson(main, params.lessonId, params.subject, params.grade);
                break;
            case 'quiz':
                Quiz.renderQuiz(main, params.unitId, params.subject, params.grade);
                break;
            case 'badges':
                Gamification.renderBadges(main);
                break;
            case 'profile':
                Progress.renderProfile(main);
                break;
            case 'teacher':
                this.renderTeacherDashboard(main);
                break;
            case 'teacher-student':
                this.renderTeacherStudentReport(main, params.studentId);
                break;
            case 'about':
                this.renderAbout(main);
                break;
            case 'tutor':
                Tutor.renderFullPage(main);
                break;
            case 'ai-studio':
                Generate.renderStudio(main);
                break;
            case 'flashcards-home':
                Flashcards.renderHome(main);
                break;
            case 'flashcards-study':
                Flashcards.renderStudy(main, params.subject, params.grade);
                break;
            case 'vocabulary':
                Vocabulary.renderPage(main);
                break;
            case 'bookmarks':
                this.renderBookmarks(main);
                break;
            case 'notes':
                this.renderNotes(main);
                break;
            default:
                main.innerHTML = '<div class="page-container"><h1>Page not found</h1></div>';
        }

        // Update tutor context for proactive behavior
        if (typeof Tutor !== 'undefined' && Tutor.updateForPage) {
            Tutor.updateForPage(page, params);
        }
    },

    /** Render Login / Landing Page */
    renderLogin(container) {
        document.getElementById('main-nav').classList.add('hidden');
        document.getElementById('tutor-toggle').classList.add('hidden');
        const footer = document.getElementById('app-footer');
        if (footer) footer.classList.add('hidden');
        container.innerHTML = `
            <div class="landing-page">
                <!-- Hero Section -->
                <section class="landing-hero">
                    <div class="landing-hero-bg"></div>
                    <div class="landing-hero-content">
                        <svg class="landing-owl" viewBox="0 0 120 120" width="120" height="120">
                            <circle cx="60" cy="60" r="55" fill="rgba(255,255,255,0.2)"/>
                            <circle cx="42" cy="48" r="16" fill="white"/>
                            <circle cx="78" cy="48" r="16" fill="white"/>
                            <circle cx="42" cy="48" r="8" fill="#333"/>
                            <circle cx="78" cy="48" r="8" fill="#333"/>
                            <circle cx="45" cy="45" r="3" fill="white"/>
                            <circle cx="81" cy="45" r="3" fill="white"/>
                            <polygon points="60,58 52,70 68,70" fill="#F39C12"/>
                            <path d="M25,30 Q38,10 48,30" fill="rgba(255,255,255,0.2)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
                            <path d="M72,30 Q82,10 95,30" fill="rgba(255,255,255,0.2)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
                            <ellipse cx="60" cy="90" rx="30" ry="12" fill="rgba(255,255,255,0.15)"/>
                        </svg>
                        <h1 class="landing-title">LearnQuest</h1>
                        <p class="landing-slogan">Learn Without Limits</p>
                        <p class="landing-tagline">Free, offline, AI-powered education for grades K-12</p>
                    </div>
                </section>

                <!-- Login Card -->
                <section class="landing-login-section">
                    <div class="landing-login-card">
                        <h2>Welcome!</h2>
                        <p class="landing-login-subtitle">Log in to start your learning adventure</p>
                        <form onsubmit="App.handleLogin(event)" class="login-form">
                            <div class="form-group">
                                <label for="login-name">Your Name</label>
                                <input type="text" id="login-name" placeholder="Enter your name" required autofocus>
                            </div>
                            <div class="form-group">
                                <label for="login-pin">PIN</label>
                                <input type="password" id="login-pin" placeholder="Enter your PIN" maxlength="10" required>
                            </div>
                            <div id="login-error" class="error-msg hidden"></div>
                            <button type="submit" class="btn btn-primary btn-large landing-login-btn">Start Learning!</button>
                        </form>
                        <p class="landing-teacher-link">Teacher? Use name <strong>teacher</strong> and your PIN to access the dashboard.</p>
                    </div>
                </section>

                <!-- Feature Cards -->
                <section class="landing-features">
                    <h2 class="landing-section-title">Everything You Need to Learn</h2>
                    <div class="landing-features-grid">
                        <div class="landing-feature-card">
                            <div class="landing-feature-icon">&#129302;</div>
                            <h3>AI Tutor</h3>
                            <p>Get help from a personal AI tutor that explains things in a way you understand</p>
                        </div>
                        <div class="landing-feature-card">
                            <div class="landing-feature-icon">&#128218;</div>
                            <h3>4 Subjects</h3>
                            <p>Math, Science, English, and Social Studies from Kindergarten through 12th grade</p>
                        </div>
                        <div class="landing-feature-card">
                            <div class="landing-feature-icon">&#127942;</div>
                            <h3>Games &amp; Rewards</h3>
                            <p>Earn XP, level up, collect badges, and keep your learning streak going</p>
                        </div>
                        <div class="landing-feature-card">
                            <div class="landing-feature-icon">&#128421;</div>
                            <h3>Works Offline</h3>
                            <p>Runs entirely from a USB drive &mdash; no internet needed after setup</p>
                        </div>
                    </div>
                </section>

                <!-- How It Works -->
                <section class="landing-how">
                    <h2 class="landing-section-title">How It Works</h2>
                    <div class="landing-steps">
                        <div class="landing-step">
                            <div class="landing-step-num">1</div>
                            <h3>Log In</h3>
                            <p>Ask your teacher for your name and PIN, then log in above</p>
                        </div>
                        <div class="landing-step-arrow">&#10132;</div>
                        <div class="landing-step">
                            <div class="landing-step-num">2</div>
                            <h3>Pick a Subject</h3>
                            <p>Choose Math, Science, English, or Social Studies</p>
                        </div>
                        <div class="landing-step-arrow">&#10132;</div>
                        <div class="landing-step">
                            <div class="landing-step-num">3</div>
                            <h3>Start Learning</h3>
                            <p>Read lessons, solve problems, earn XP, and level up!</p>
                        </div>
                    </div>
                </section>

                <!-- Landing Footer -->
                <footer class="landing-footer">
                    <p>Learn Without Limits &mdash; Free Education for All</p>
                    <p class="landing-footer-credit">Created by <strong>Diamond Bar High School Vibe Coding Club</strong></p>
                </footer>
            </div>
        `;
    },

    /** Handle login form submission */
    async handleLogin(event) {
        event.preventDefault();
        const name = document.getElementById('login-name').value.trim();
        const pin = document.getElementById('login-pin').value;
        const errorEl = document.getElementById('login-error');
        errorEl.classList.add('hidden');

        try {
            const data = await this.api('/api/auth/login', {
                method: 'POST',
                body: { name, pin }
            });
            this.state.user = data.user;
            this.onLoginSuccess();
        } catch (err) {
            errorEl.textContent = err.message || 'Login failed';
            errorEl.classList.remove('hidden');
        }
    },

    /** Render Home Page */
    async renderHome(container) {
        const user = this.state.user;
        if (!user) return this.navigate('login');

        if (user.role === 'teacher') {
            return this.navigate('teacher');
        }

        container.innerHTML = `
            <div class="page-container home-page">
                <div class="welcome-section">
                    <div class="welcome-text">
                        <h1>Welcome back, ${this.escapeHtml(user.name)}! 👋</h1>
                        <p>Ready to learn something awesome today?</p>
                    </div>
                    <div class="streak-card">
                        <div class="streak-flame ${user.streak_days > 0 ? 'active' : ''}">🔥</div>
                        <div class="streak-info">
                            <span class="streak-count">${user.streak_days || 0}</span>
                            <span class="streak-label">Day Streak</span>
                        </div>
                    </div>
                </div>

                <div class="xp-section">
                    <div class="level-badge">Level ${user.level || 1}</div>
                    <div class="xp-bar-container">
                        <div class="xp-bar" id="home-xp-bar"></div>
                    </div>
                    <div class="xp-text">${user.xp || 0} XP</div>
                </div>

                <div class="daily-challenge-section" id="daily-challenge-area">
                    <h2>⚡ Daily Challenge</h2>
                    <div id="daily-challenge-content">Loading...</div>
                </div>

                <h2>Choose a Subject</h2>
                <div class="subject-cards">
                    <div class="subject-card math" onclick="App.navigate('units', {subject:'math', grade:${user.grade}})">
                        <div class="subject-icon">📐</div>
                        <h3>Math</h3>
                        <div class="progress-ring" id="progress-math"></div>
                    </div>
                    <div class="subject-card science" onclick="App.navigate('units', {subject:'science', grade:${user.grade}})">
                        <div class="subject-icon">🔬</div>
                        <h3>Science</h3>
                        <div class="progress-ring" id="progress-science"></div>
                    </div>
                    <div class="subject-card ela" onclick="App.navigate('units', {subject:'ela', grade:${user.grade}})">
                        <div class="subject-icon">📚</div>
                        <h3>English</h3>
                        <div class="progress-ring" id="progress-ela"></div>
                    </div>
                    <div class="subject-card social" onclick="App.navigate('units', {subject:'social_studies', grade:${user.grade}})">
                        <div class="subject-icon">🌍</div>
                        <h3>Social Studies</h3>
                        <div class="progress-ring" id="progress-social"></div>
                    </div>
                </div>

                <div class="recent-badges-section" id="recent-badges">
                </div>
            </div>
        `;

        // Load XP bar
        Progress.updateXpBar('home-xp-bar', user.xp, user.level);

        // Load daily challenge
        Progress.loadDailyChallenge();

        // Load progress rings
        Progress.loadSubjectProgress();
    },

    /** Render Subjects Page */
    renderSubjects(container) {
        const user = this.state.user;
        if (!user) return this.navigate('login');

        container.innerHTML = `
            <div class="page-container subjects-page">
                <h1>Choose a Subject</h1>
                <p>Pick a subject to start your learning adventure!</p>
                <div class="subject-grid">
                    <div class="subject-card-large math" onclick="App.navigate('units', {subject:'math', grade:${user.grade}})">
                        <div class="subject-icon-large">📐</div>
                        <h2>Mathematics</h2>
                        <p>Numbers, shapes, and problem solving</p>
                        <div class="subject-progress" id="subj-progress-math"></div>
                    </div>
                    <div class="subject-card-large science" onclick="App.navigate('units', {subject:'science', grade:${user.grade}})">
                        <div class="subject-icon-large">🔬</div>
                        <h2>Science</h2>
                        <p>Discover how the world works</p>
                        <div class="subject-progress" id="subj-progress-science"></div>
                    </div>
                    <div class="subject-card-large ela" onclick="App.navigate('units', {subject:'ela', grade:${user.grade}})">
                        <div class="subject-icon-large">📚</div>
                        <h2>English Language Arts</h2>
                        <p>Reading, writing, and communication</p>
                        <div class="subject-progress" id="subj-progress-ela"></div>
                    </div>
                    <div class="subject-card-large social" onclick="App.navigate('units', {subject:'social_studies', grade:${user.grade}})">
                        <div class="subject-icon-large">🌍</div>
                        <h2>Social Studies</h2>
                        <p>History, geography, and civics</p>
                        <div class="subject-progress" id="subj-progress-social"></div>
                    </div>
                </div>
            </div>
        `;
    },

    /** Render Teacher Dashboard */
    async renderTeacherDashboard(container) {
        if (!this.state.user || this.state.user.role !== 'teacher') {
            return this.navigate('home');
        }

        container.innerHTML = `
            <div class="page-container teacher-page">
                <h1>Teacher Dashboard</h1>
                <div class="teacher-tabs">
                    <button class="tab-btn active" onclick="Teacher.showTab('students')">Students</button>
                    <button class="tab-btn" onclick="Teacher.showTab('add-student')">Add Student</button>
                    <button class="tab-btn" onclick="Teacher.showTab('classroom')">Classroom Setup</button>
                    <button class="tab-btn" onclick="Teacher.showTab('settings')">Settings</button>
                </div>
                <div id="teacher-content">Loading...</div>
            </div>
        `;
        Teacher.loadStudents();
    },

    async renderTeacherStudentReport(container, studentId) {
        if (!this.state.user || this.state.user.role !== 'teacher') {
            return this.navigate('home');
        }
        container.innerHTML = `
            <div class="page-container teacher-page">
                <button class="btn btn-secondary" onclick="App.navigate('teacher')">← Back to Dashboard</button>
                <div id="student-report">Loading...</div>
            </div>
        `;
        Teacher.loadStudentReport(studentId);
    },

    /** Logout */
    async logout() {
        try {
            await this.api('/api/auth/logout', { method: 'POST' });
        } catch (e) { /* ignore */ }
        this.state.user = null;
        this.navigate('login');
    },

    /** Toggle dark mode */
    toggleDarkMode() {
        this.state.darkMode = !this.state.darkMode;
        document.body.classList.toggle('dark-mode', this.state.darkMode);
        localStorage.setItem('darkMode', this.state.darkMode);
    },

    /** Toggle user dropdown */
    toggleUserMenu() {
        document.getElementById('user-dropdown').classList.toggle('hidden');
    },

    /** Update nav stats */
    updateNavStats() {
        if (this.state.user) {
            document.getElementById('nav-xp-value').textContent = this.state.user.xp || 0;
            document.getElementById('nav-streak-value').textContent = this.state.user.streak_days || 0;
        }
    },

    /** Show toast notification */
    showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('show'));
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    /** Escape HTML */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /** Refresh user data from server */
    async refreshUser() {
        try {
            const data = await this.api('/api/auth/session');
            if (data.user) {
                this.state.user = data.user;
                this.updateNavStats();
            }
        } catch (e) { /* ignore */ }
    },

    /** Render About Page */
    renderAbout(container) {
        container.innerHTML = `
            <div class="page-container about-page">
                <div class="about-hero">
                    <svg class="owl-icon-large" viewBox="0 0 120 120" width="100" height="100">
                        <circle cx="60" cy="60" r="55" fill="#4A90D9"/>
                        <circle cx="42" cy="48" r="16" fill="white"/>
                        <circle cx="78" cy="48" r="16" fill="white"/>
                        <circle cx="42" cy="48" r="8" fill="#333"/>
                        <circle cx="78" cy="48" r="8" fill="#333"/>
                        <circle cx="45" cy="45" r="3" fill="white"/>
                        <circle cx="81" cy="45" r="3" fill="white"/>
                        <polygon points="60,58 52,70 68,70" fill="#F39C12"/>
                        <path d="M25,30 Q38,10 48,30" fill="#4A90D9" stroke="#3a7bc8" stroke-width="2"/>
                        <path d="M72,30 Q82,10 95,30" fill="#4A90D9" stroke="#3a7bc8" stroke-width="2"/>
                        <ellipse cx="60" cy="90" rx="30" ry="12" fill="#3a7bc8"/>
                    </svg>
                    <h1>LearnQuest</h1>
                    <p class="about-slogan">Learn Without Limits &mdash; Free Education for All</p>
                </div>

                <div class="about-section">
                    <h2>Our Mission</h2>
                    <p>We believe education should be free, easy, and accessible for all. LearnQuest is a fully offline K-8 tutoring platform that runs from a USB drive &mdash; no internet required. Plug it in, start learning.</p>
                </div>

                <div class="about-section">
                    <h2>Created By</h2>
                    <p class="about-credit-name">Diamond Bar High School Vibe Coding Club</p>
                    <p>Built with passion by students, for students.</p>
                </div>

                <div class="about-section">
                    <h2>What's Inside</h2>
                    <div class="about-features">
                        <div class="about-feature"><span>4 Subjects</span> Math, Science, ELA, Social Studies (K-12)</div>
                        <div class="about-feature"><span>AI Tutor</span> Powered by a local AI that runs on your computer</div>
                        <div class="about-feature"><span>AI Studio</span> Generate custom lessons, quizzes, and flashcards</div>
                        <div class="about-feature"><span>Gamification</span> XP, levels, badges, streaks, and leaderboards</div>
                        <div class="about-feature"><span>Flashcards</span> Spaced repetition learning with flip cards</div>
                        <div class="about-feature"><span>Study Timer</span> Pomodoro timer to stay focused</div>
                        <div class="about-feature"><span>Teacher Tools</span> Student management, reports, CSV export</div>
                        <div class="about-feature"><span>Fully Offline</span> No internet needed after setup</div>
                    </div>
                </div>

                <div class="about-section">
                    <h2>Tech Stack</h2>
                    <p>Python + Flask backend, vanilla JavaScript SPA, SQLite database, Phi-3 Mini via Ollama for AI. Zero external dependencies at runtime.</p>
                </div>
            </div>
        `;
    },

    /** Show confirmation dialog */
    showConfirm(message, onConfirm) {
        const modal = document.getElementById('confirm-modal');
        document.getElementById('confirm-message').textContent = message;
        const okBtn = document.getElementById('confirm-ok-btn');
        this._confirmCallback = onConfirm;
        okBtn.onclick = () => this.closeConfirm(true);
        modal.classList.remove('hidden');
    },

    /** Close confirmation dialog */
    closeConfirm(confirmed) {
        document.getElementById('confirm-modal').classList.add('hidden');
        if (confirmed && this._confirmCallback) {
            this._confirmCallback();
        }
        this._confirmCallback = null;
    },

    /** Search handling */
    _searchTimeout: null,
    handleSearch(event) {
        clearTimeout(this._searchTimeout);
        const query = event.target.value.trim();
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }
        this._searchTimeout = setTimeout(() => this.performSearch(query), 300);
    },

    async performSearch(query) {
        try {
            const data = await this.api(`/api/search?q=${encodeURIComponent(query)}`);
            const dropdown = document.getElementById('search-results-dropdown');
            if (!data.results || data.results.length === 0) {
                dropdown.innerHTML = '<div class="search-no-results">No results found</div>';
                dropdown.classList.remove('hidden');
                return;
            }
            dropdown.innerHTML = data.results.slice(0, 8).map(r => `
                <div class="search-result-item" onmousedown="App.navigate('lesson', {lessonId:'${r.lesson_id}', subject:'${r.subject}', grade:${r.grade}})">
                    <span class="search-subject-tag ${r.subject}">${r.subject}</span>
                    <span class="search-title">${this.escapeHtml(r.title)}</span>
                    <span class="search-context">${this.escapeHtml(r.context || '')}</span>
                </div>
            `).join('');
            dropdown.classList.remove('hidden');
        } catch (e) {
            /* ignore search errors */
        }
    },

    showSearchResults() {
        const input = document.getElementById('nav-search-input');
        if (input && input.value.trim().length >= 2) {
            this.performSearch(input.value.trim());
        }
    },

    hideSearchResults() {
        document.getElementById('search-results-dropdown')?.classList.add('hidden');
    },

    /** Render Bookmarks Page */
    async renderBookmarks(container) {
        const user = this.state.user;
        if (!user) return this.navigate('login');
        try {
            const data = await this.api('/api/bookmarks');
            container.innerHTML = `
                <div class="page-container">
                    <h1>My Bookmarks</h1>
                    ${(data.bookmarks && data.bookmarks.length > 0) ? `
                        <div class="bookmarks-list">
                            ${data.bookmarks.map(b => `
                                <div class="bookmark-item" onclick="App.navigate('lesson', {lessonId:'${b.lesson_id}', subject:'${b.subject}', grade:${b.grade}})">
                                    <span class="bookmark-star">&#9733;</span>
                                    <span class="bookmark-title">${this.escapeHtml(b.lesson_title || b.lesson_id)}</span>
                                    <span class="bookmark-subject ${b.subject}">${b.subject}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p>No bookmarks yet. Click the star on any lesson to bookmark it!</p>'}
                </div>
            `;
        } catch (e) {
            container.innerHTML = '<div class="page-container"><p>Error loading bookmarks.</p></div>';
        }
    },

    /** Render Notes Page */
    async renderNotes(container) {
        const user = this.state.user;
        if (!user) return this.navigate('login');
        try {
            const data = await this.api('/api/notes');
            container.innerHTML = `
                <div class="page-container">
                    <h1>My Notes</h1>
                    ${(data.notes && data.notes.length > 0) ? `
                        <div class="notes-list">
                            ${data.notes.map(n => `
                                <div class="note-card">
                                    <div class="note-header">
                                        <strong>${this.escapeHtml(n.lesson_title || n.lesson_id || 'General')}</strong>
                                        <span class="note-date">${n.updated_at || ''}</span>
                                    </div>
                                    <p class="note-body">${this.escapeHtml(n.content)}</p>
                                    <button class="btn btn-secondary btn-sm" onclick="App.deleteNote(${n.id})">Delete</button>
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p>No notes yet. Take notes while studying lessons!</p>'}
                </div>
            `;
        } catch (e) {
            container.innerHTML = '<div class="page-container"><p>Error loading notes.</p></div>';
        }
    },

    async deleteNote(noteId) {
        try {
            await this.api(`/api/notes/${noteId}`, { method: 'DELETE' });
            this.showToast('Note deleted', 'success');
            this.navigate('notes');
        } catch (e) {
            this.showToast('Error deleting note', 'error');
        }
    }
};

const Teacher = {
    async loadStudents() {
        try {
            const data = await App.api('/api/teacher/students');
            const el = document.getElementById('teacher-content');
            if (!data.students || data.students.length === 0) {
                el.innerHTML = '<p>No students yet. Add a student to get started!</p>';
                return;
            }
            el.innerHTML = `
                <div class="students-grid">
                    ${data.students.map(s => `
                        <div class="student-card">
                            <div class="student-card-main" onclick="App.navigate('teacher-student', {studentId: ${s.id}})">
                                <div class="student-avatar">🦉</div>
                                <div class="student-info">
                                    <h3>${App.escapeHtml(s.name)}</h3>
                                    <p>Grade ${s.grade} · Level ${s.level} · ${s.xp} XP</p>
                                    <p>Streak: ${s.streak_days} days</p>
                                </div>
                            </div>
                            <div class="student-actions">
                                <button class="btn-icon" onclick="event.stopPropagation();Teacher.editStudent(${s.id})" title="Edit">&#9998;</button>
                                <button class="btn-icon btn-icon-danger" onclick="event.stopPropagation();Teacher.deleteStudent(${s.id},'${App.escapeHtml(s.name).replace(/'/g, "\\'")}')" title="Delete">&#128465;</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div style="margin-top:1rem">
                    <button class="btn btn-secondary" onclick="Teacher.exportCSV()">Export CSV</button>
                </div>
            `;
        } catch (err) {
            document.getElementById('teacher-content').innerHTML = `<p class="error-msg">Error loading students: ${err.message}</p>`;
        }
    },

    async showTab(tab) {
        const tabMap = { 'Students': 'students', 'Add Student': 'add-student', 'Classroom Setup': 'classroom', 'Settings': 'settings' };
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.toggle('active', tabMap[b.textContent] === tab);
        });
        const el = document.getElementById('teacher-content');
        if (tab === 'students') {
            this.loadStudents();
        } else if (tab === 'add-student') {
            el.innerHTML = `
                <div class="add-student-form">
                    <h2>Add New Student</h2>
                    <form onsubmit="Teacher.addStudent(event)">
                        <div class="form-group">
                            <label>Student Name</label>
                            <input type="text" id="new-student-name" required>
                        </div>
                        <div class="form-group">
                            <label>PIN</label>
                            <input type="password" id="new-student-pin" maxlength="10" required>
                        </div>
                        <div class="form-group">
                            <label>Grade</label>
                            <select id="new-student-grade">
                                <option value="0">Kindergarten</option>
                                ${[1,2,3,4,5,6,7,8,9,10,11,12].map(g => `<option value="${g}">Grade ${g}</option>`).join('')}
                            </select>
                        </div>
                        <div id="add-student-error" class="error-msg hidden"></div>
                        <button type="submit" class="btn btn-primary">Add Student</button>
                    </form>
                </div>
            `;
        } else if (tab === 'classroom') {
            this.loadClassroomSetup(el);
        } else if (tab === 'settings') {
            this.loadSettings(el);
        }
    },

    /** Edit student modal */
    async editStudent(id) {
        try {
            const data = await App.api(`/api/teacher/report/${id}`);
            const s = data.student;
            const el = document.getElementById('teacher-content');
            el.innerHTML = `
                <div class="add-student-form">
                    <h2>Edit Student: ${App.escapeHtml(s.name)}</h2>
                    <form onsubmit="Teacher.saveStudent(event, ${id})">
                        <div class="form-group">
                            <label>Student Name</label>
                            <input type="text" id="edit-student-name" value="${App.escapeHtml(s.name)}" required>
                        </div>
                        <div class="form-group">
                            <label>New PIN (leave blank to keep current)</label>
                            <input type="password" id="edit-student-pin" maxlength="10" placeholder="Leave blank to keep">
                        </div>
                        <div class="form-group">
                            <label>Grade</label>
                            <select id="edit-student-grade">
                                <option value="0" ${s.grade === 0 ? 'selected' : ''}>Kindergarten</option>
                                ${[1,2,3,4,5,6,7,8].map(g => `<option value="${g}" ${s.grade === g ? 'selected' : ''}>Grade ${g}</option>`).join('')}
                            </select>
                        </div>
                        <div id="edit-student-error" class="error-msg hidden"></div>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                        <button type="button" class="btn btn-secondary" onclick="Teacher.showTab('students')">Cancel</button>
                    </form>
                </div>
            `;
        } catch (err) {
            App.showToast('Error loading student: ' + err.message, 'error');
        }
    },

    async saveStudent(event, id) {
        event.preventDefault();
        const errEl = document.getElementById('edit-student-error');
        errEl.classList.add('hidden');
        const body = {
            name: document.getElementById('edit-student-name').value.trim(),
            grade: parseInt(document.getElementById('edit-student-grade').value)
        };
        const pin = document.getElementById('edit-student-pin').value;
        if (pin) body.pin = pin;
        try {
            await App.api(`/api/teacher/student/${id}`, { method: 'PUT', body });
            App.showToast('Student updated!', 'success');
            this.showTab('students');
        } catch (err) {
            errEl.textContent = err.message;
            errEl.classList.remove('hidden');
        }
    },

    /** Delete student with confirmation */
    deleteStudent(id, name) {
        App.showConfirm(`Delete student "${name}" and all their data? This cannot be undone.`, async () => {
            try {
                await App.api(`/api/teacher/student/${id}`, { method: 'DELETE' });
                App.showToast('Student deleted', 'success');
                this.loadStudents();
            } catch (err) {
                App.showToast('Error: ' + err.message, 'error');
            }
        });
    },

    /** Classroom Setup tab */
    async loadClassroomSetup(el) {
        try {
            const data = await App.api('/api/teacher/network-info');
            el.innerHTML = `
                <div class="classroom-setup">
                    <h2>Classroom Setup</h2>
                    <p>Students can connect to LearnQuest from their own devices using your local network.</p>

                    <div class="classroom-info-card">
                        <h3>Connection URL</h3>
                        <div class="classroom-url">${App.escapeHtml(data.url)}</div>
                        <p class="classroom-hint">Share this URL with your students. They can type it into their browser's address bar.</p>
                    </div>

                    <div class="classroom-info-card">
                        <h3>QR Code</h3>
                        <div id="classroom-qr"></div>
                        <p class="classroom-hint">Students can scan this QR code with their device's camera.</p>
                    </div>

                    <div class="classroom-info-card">
                        <h3>Instructions for Students</h3>
                        <ol class="classroom-steps">
                            <li>Connect to the same WiFi network as this computer</li>
                            <li>Open a web browser (Chrome, Safari, Firefox, etc.)</li>
                            <li>Type <strong>${App.escapeHtml(data.url)}</strong> in the address bar</li>
                            <li>Log in with your name and PIN</li>
                        </ol>
                    </div>
                </div>
            `;
            // Generate QR code
            if (typeof QRCode !== 'undefined') {
                QRCode.generate(data.url, document.getElementById('classroom-qr'));
            } else {
                document.getElementById('classroom-qr').innerHTML = `<p class="qr-fallback">${App.escapeHtml(data.url)}</p>`;
            }
        } catch (err) {
            el.innerHTML = `<p class="error-msg">Error: ${err.message}</p>`;
        }
    },

    async addStudent(event) {
        event.preventDefault();
        const errEl = document.getElementById('add-student-error');
        errEl.classList.add('hidden');
        try {
            await App.api('/api/auth/register', {
                method: 'POST',
                body: {
                    name: document.getElementById('new-student-name').value.trim(),
                    pin: document.getElementById('new-student-pin').value,
                    grade: parseInt(document.getElementById('new-student-grade').value)
                }
            });
            App.showToast('Student added!', 'success');
            this.showTab('students');
        } catch (err) {
            errEl.textContent = err.message;
            errEl.classList.remove('hidden');
        }
    },

    async loadSettings(el) {
        try {
            const data = await App.api('/api/teacher/settings');
            el.innerHTML = `
                <div class="settings-form">
                    <h2>Platform Settings</h2>
                    <div class="setting-row">
                        <label>Leaderboard</label>
                        <input type="checkbox" id="set-leaderboard" ${data.leaderboard_enabled === 'true' ? 'checked' : ''}>
                    </div>
                    <div class="setting-row">
                        <label>Quiz Timer</label>
                        <input type="checkbox" id="set-timer" ${data.quiz_timer_enabled === 'true' ? 'checked' : ''}>
                    </div>
                    <div class="setting-row">
                        <label>Timer Seconds</label>
                        <input type="number" id="set-timer-seconds" value="${data.quiz_timer_seconds || 300}" min="60" max="3600">
                    </div>
                    <div class="setting-row">
                        <label>Gamification</label>
                        <input type="checkbox" id="set-gamification" ${data.gamification_enabled === 'true' ? 'checked' : ''}>
                    </div>
                    <button class="btn btn-primary" onclick="Teacher.saveSettings()">Save Settings</button>
                </div>
            `;
        } catch (err) {
            el.innerHTML = `<p class="error-msg">Error: ${err.message}</p>`;
        }
    },

    async saveSettings() {
        try {
            await App.api('/api/teacher/settings', {
                method: 'POST',
                body: {
                    leaderboard_enabled: document.getElementById('set-leaderboard').checked ? 'true' : 'false',
                    quiz_timer_enabled: document.getElementById('set-timer').checked ? 'true' : 'false',
                    quiz_timer_seconds: document.getElementById('set-timer-seconds').value,
                    gamification_enabled: document.getElementById('set-gamification').checked ? 'true' : 'false'
                }
            });
            App.showToast('Settings saved!', 'success');
        } catch (err) {
            App.showToast('Error saving settings: ' + err.message, 'error');
        }
    },

    async loadStudentReport(studentId) {
        try {
            const data = await App.api(`/api/teacher/report/${studentId}`);
            const el = document.getElementById('student-report');
            const s = data.student;
            el.innerHTML = `
                <h2>${App.escapeHtml(s.name)}'s Report</h2>
                <div class="report-stats">
                    <div class="stat-card"><div class="stat-value">${s.grade === 0 ? 'K' : s.grade}</div><div class="stat-label">Grade</div></div>
                    <div class="stat-card"><div class="stat-value">${s.level}</div><div class="stat-label">Level</div></div>
                    <div class="stat-card"><div class="stat-value">${s.xp}</div><div class="stat-label">XP</div></div>
                    <div class="stat-card"><div class="stat-value">${s.streak_days}</div><div class="stat-label">Streak</div></div>
                </div>
                <h3>Lessons Completed</h3>
                <div class="report-table-wrap">
                    <table class="report-table">
                        <tr><th>Subject</th><th>Completed</th><th>Avg Score</th></tr>
                        ${(data.progress || []).map(p => `
                            <tr><td>${p.subject}</td><td>${p.completed}</td><td>${p.avg_score ? p.avg_score.toFixed(0) + '%' : '-'}</td></tr>
                        `).join('')}
                    </table>
                </div>
                <h3>Recent Quizzes</h3>
                <div class="report-table-wrap">
                    <table class="report-table">
                        <tr><th>Quiz</th><th>Subject</th><th>Score</th><th>Date</th></tr>
                        ${(data.quizzes || []).map(q => `
                            <tr><td>${q.quiz_id}</td><td>${q.subject}</td><td>${q.correct_answers}/${q.total_questions}</td><td>${q.completed_at || ''}</td></tr>
                        `).join('')}
                    </table>
                </div>
                <h3>Badges Earned</h3>
                <div class="badges-list">
                    ${(data.badges || []).map(b => `<span class="badge-item">🏆 ${b.badge_name}</span>`).join('') || '<p>No badges yet</p>'}
                </div>
            `;
        } catch (err) {
            document.getElementById('student-report').innerHTML = `<p class="error-msg">Error: ${err.message}</p>`;
        }
    },

    async exportCSV() {
        try {
            const resp = await fetch('/api/teacher/export', { method: 'POST' });
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'learnquest_progress.csv';
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            App.showToast('Export failed: ' + err.message, 'error');
        }
    }
};

// Start app
document.addEventListener('DOMContentLoaded', () => App.init());
