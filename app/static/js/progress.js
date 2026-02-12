/**
 * LearnQuest - Progress Tracking & XP System
 */

const Progress = {
    /** Level thresholds and names */
    levels: [
        { level: 1, xp: 0, name: 'Number Newbie' },
        { level: 2, xp: 50, name: 'Curious Cub' },
        { level: 3, xp: 120, name: 'Eager Explorer' },
        { level: 4, xp: 200, name: 'Quick Thinker' },
        { level: 5, xp: 300, name: 'Star Student' },
        { level: 6, xp: 420, name: 'Bright Spark' },
        { level: 7, xp: 560, name: 'Knowledge Keeper' },
        { level: 8, xp: 720, name: 'Problem Solver' },
        { level: 9, xp: 900, name: 'Brain Builder' },
        { level: 10, xp: 1100, name: 'Super Scholar' },
        { level: 11, xp: 1320, name: 'Fact Finder' },
        { level: 12, xp: 1560, name: 'Logic Legend' },
        { level: 13, xp: 1820, name: 'Wisdom Warrior' },
        { level: 14, xp: 2100, name: 'Mind Master' },
        { level: 15, xp: 2400, name: 'Fraction Fighter' },
        { level: 16, xp: 2720, name: 'Data Detective' },
        { level: 17, xp: 3060, name: 'Science Sage' },
        { level: 18, xp: 3420, name: 'Reading Ranger' },
        { level: 19, xp: 3800, name: 'History Hero' },
        { level: 20, xp: 4200, name: 'Equation Expert' },
        { level: 21, xp: 4620, name: 'Discovery Dude' },
        { level: 22, xp: 5060, name: 'Chapter Champion' },
        { level: 23, xp: 5520, name: 'Graph Guru' },
        { level: 24, xp: 6000, name: 'Vocab Victor' },
        { level: 25, xp: 6500, name: 'Halfway Hero' },
        { level: 26, xp: 7020, name: 'Pattern Pro' },
        { level: 27, xp: 7560, name: 'Research Rookie' },
        { level: 28, xp: 8120, name: 'Theory Thinker' },
        { level: 29, xp: 8700, name: 'Number Ninja' },
        { level: 30, xp: 9300, name: 'Knowledge Knight' },
        { level: 31, xp: 9920, name: 'Geometry Genius' },
        { level: 32, xp: 10560, name: 'Word Wizard' },
        { level: 33, xp: 11220, name: 'Lab Leader' },
        { level: 34, xp: 11900, name: 'Map Master' },
        { level: 35, xp: 12600, name: 'Algebra Ace' },
        { level: 36, xp: 13320, name: 'Essay Expert' },
        { level: 37, xp: 14060, name: 'Atom Adventurer' },
        { level: 38, xp: 14820, name: 'Civics Champion' },
        { level: 39, xp: 15600, name: 'Formula Finder' },
        { level: 40, xp: 16400, name: 'Literature Lord' },
        { level: 41, xp: 17220, name: 'Planet Pioneer' },
        { level: 42, xp: 18060, name: 'Debate Duke' },
        { level: 43, xp: 18920, name: 'Calculus Cadet' },
        { level: 44, xp: 19800, name: 'Grammar Guardian' },
        { level: 45, xp: 20700, name: 'Element Explorer' },
        { level: 46, xp: 21620, name: 'Timeline Titan' },
        { level: 47, xp: 22560, name: 'Proof Pioneer' },
        { level: 48, xp: 23520, name: 'Scholar Supreme' },
        { level: 49, xp: 24500, name: 'Genius General' },
        { level: 50, xp: 25000, name: 'LearnQuest Legend' }
    ],

    /** Get level info for XP amount */
    getLevelInfo(xp) {
        let current = this.levels[0];
        let next = this.levels[1];
        for (let i = this.levels.length - 1; i >= 0; i--) {
            if (xp >= this.levels[i].xp) {
                current = this.levels[i];
                next = this.levels[i + 1] || this.levels[i];
                break;
            }
        }
        const xpInLevel = xp - current.xp;
        const xpNeeded = next.xp - current.xp;
        const progress = xpNeeded > 0 ? (xpInLevel / xpNeeded) * 100 : 100;
        return { ...current, next, xpInLevel, xpNeeded, progress };
    },

    /** Update XP bar */
    updateXpBar(elementId, xp, level) {
        const info = this.getLevelInfo(xp);
        const bar = document.getElementById(elementId);
        if (bar) {
            bar.style.width = info.progress + '%';
            bar.title = `${info.name} - ${info.xpInLevel}/${info.xpNeeded} XP to next level`;
        }
    },

    /** Load daily challenge */
    async loadDailyChallenge() {
        const container = document.getElementById('daily-challenge-content');
        if (!container) return;

        try {
            const data = await App.api('/api/daily-challenge');
            if (data.completed) {
                container.innerHTML = `
                    <div class="challenge-completed">
                        <p>✅ You already completed today's challenge!</p>
                        <p>Come back tomorrow for a new one.</p>
                    </div>
                `;
                return;
            }

            const q = data.question;
            container.innerHTML = `
                <div class="challenge-card">
                    <div class="challenge-subject">${data.subject}</div>
                    <p class="challenge-question">${App.escapeHtml(q.question)}</p>
                    ${q.type === 'multiple_choice' ? `
                        <div class="mc-options">
                            ${(q.options || []).map((opt, i) => `
                                <button class="mc-option" onclick="Progress.submitDailyChallenge(${i})">${App.escapeHtml(String(opt))}</button>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="fill-in-area">
                            <input type="text" id="daily-answer" class="answer-input" placeholder="Your answer...">
                            <button class="btn btn-primary" onclick="Progress.submitDailyChallengeText()">Submit</button>
                        </div>
                    `}
                    <div class="challenge-reward">🎁 +15 XP</div>
                </div>
            `;
        } catch (err) {
            container.innerHTML = '<p>Challenge unavailable today.</p>';
        }
    },

    /** Submit daily challenge (MC) */
    async submitDailyChallenge(answer) {
        const container = document.getElementById('daily-challenge-content');
        try {
            const data = await App.api('/api/daily-challenge/submit', {
                method: 'POST',
                body: { answer }
            });
            if (data.correct) {
                container.innerHTML = `<div class="challenge-completed"><p>🎉 Correct! +15 XP</p></div>`;
                Gamification.showXpGain(15);
                await App.refreshUser();
            } else {
                container.innerHTML = `<div class="challenge-completed"><p>❌ Not quite! The answer was: ${App.escapeHtml(String(data.correct_answer))}</p></div>`;
            }
        } catch (err) {
            container.innerHTML = `<p class="error-msg">${err.message}</p>`;
        }
    },

    /** Submit daily challenge (text) */
    async submitDailyChallengeText() {
        const input = document.getElementById('daily-answer');
        if (!input || !input.value.trim()) return;
        await this.submitDailyChallenge(input.value.trim());
    },

    /** Load subject progress rings */
    async loadSubjectProgress() {
        if (!App.state.user) return;
        try {
            const data = await App.api(`/api/progress/${App.state.user.id}`);
            const subjects = ['math', 'science', 'ela', 'social_studies'];
            subjects.forEach(sub => {
                const el = document.getElementById(`progress-${sub === 'social_studies' ? 'social' : sub}`);
                if (el) {
                    const p = data.subjects?.[sub] || { completed: 0, total: 1 };
                    const pct = p.total > 0 ? Math.round((p.completed / p.total) * 100) : 0;
                    el.innerHTML = `<span class="progress-pct">${pct}%</span>`;
                }
            });
        } catch (e) { /* ignore */ }
    },

    /** Render profile page */
    async renderProfile(container) {
        const user = App.state.user;
        if (!user) return App.navigate('login');

        const info = this.getLevelInfo(user.xp || 0);

        try {
            const progressData = await App.api(`/api/progress/${user.id}`);
            const badgesData = await App.api('/api/progress/badges');

            container.innerHTML = `
                <div class="page-container profile-page">
                    <h1>My Profile</h1>
                    <div class="profile-header">
                        <div class="profile-avatar">🦉</div>
                        <div class="profile-info">
                            <h2>${App.escapeHtml(user.name)}</h2>
                            <p>Grade ${user.grade === 0 ? 'K' : user.grade}</p>
                            <div class="level-info">
                                <span class="level-badge">Level ${info.level}</span>
                                <span class="level-name">${info.name}</span>
                            </div>
                        </div>
                    </div>

                    <div class="profile-stats">
                        <div class="stat-card"><div class="stat-value">${user.xp || 0}</div><div class="stat-label">Total XP</div></div>
                        <div class="stat-card"><div class="stat-value">${user.streak_days || 0}</div><div class="stat-label">Day Streak 🔥</div></div>
                        <div class="stat-card"><div class="stat-value">${progressData.total_lessons || 0}</div><div class="stat-label">Lessons Done</div></div>
                        <div class="stat-card"><div class="stat-value">${progressData.total_quizzes || 0}</div><div class="stat-label">Quizzes Passed</div></div>
                    </div>

                    <div class="xp-section">
                        <h3>XP Progress</h3>
                        <div class="xp-bar-container">
                            <div class="xp-bar" id="profile-xp-bar"></div>
                        </div>
                        <p>${info.xpInLevel} / ${info.xpNeeded} XP to Level ${info.next.level} (${info.next.name})</p>
                    </div>

                    <h3>My Badges</h3>
                    <div class="badges-grid">
                        ${(badgesData.earned || []).map(b => `
                            <div class="badge-card earned">
                                <div class="badge-icon">🏆</div>
                                <div class="badge-name">${App.escapeHtml(b.badge_name)}</div>
                                <div class="badge-desc">${App.escapeHtml(b.badge_description || '')}</div>
                            </div>
                        `).join('') || '<p>Complete lessons and quizzes to earn badges!</p>'}
                    </div>

                    <h3>Leaderboard</h3>
                    <div id="leaderboard-area">Loading...</div>
                </div>
            `;

            this.updateXpBar('profile-xp-bar', user.xp, user.level);
            this.loadLeaderboard();
        } catch (err) {
            container.innerHTML = `<div class="page-container"><p class="error-msg">Error: ${err.message}</p></div>`;
        }
    },

    /** Load leaderboard */
    async loadLeaderboard() {
        const el = document.getElementById('leaderboard-area');
        if (!el) return;
        try {
            const data = await App.api('/api/leaderboard');
            if (!data.leaderboard || data.leaderboard.length === 0) {
                el.innerHTML = '<p>No students yet.</p>';
                return;
            }
            el.innerHTML = `
                <div class="leaderboard">
                    ${data.leaderboard.map((s, i) => `
                        <div class="leaderboard-row ${s.id === App.state.user?.id ? 'current-user' : ''}">
                            <span class="rank">${i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '#' + (i+1)}</span>
                            <span class="lb-name">${App.escapeHtml(s.name)}</span>
                            <span class="lb-level">Lv.${s.level}</span>
                            <span class="lb-xp">${s.xp} XP</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            el.innerHTML = '<p>Leaderboard unavailable.</p>';
        }
    }
};
