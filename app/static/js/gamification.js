/**
 * LearnQuest - Gamification: Badges, Animations, Confetti
 */

const Gamification = {
    /** Badge definitions */
    badges: {
        // Subject mastery
        math_master_k: { name: 'Math Whiz (K)', desc: 'Complete all Kindergarten math units', icon: '🧮' },
        math_master_1: { name: 'Math Whiz (1st)', desc: 'Complete all Grade 1 math units', icon: '🧮' },
        math_master_2: { name: 'Math Whiz (2nd)', desc: 'Complete all Grade 2 math units', icon: '🧮' },
        math_master_3: { name: 'Math Whiz (3rd)', desc: 'Complete all Grade 3 math units', icon: '🧮' },
        math_master_4: { name: 'Math Whiz (4th)', desc: 'Complete all Grade 4 math units', icon: '🧮' },
        math_master_5: { name: 'Math Whiz (5th)', desc: 'Complete all Grade 5 math units', icon: '🧮' },
        math_master_6: { name: 'Math Whiz (6th)', desc: 'Complete all Grade 6 math units', icon: '🧮' },
        math_master_7: { name: 'Math Whiz (7th)', desc: 'Complete all Grade 7 math units', icon: '🧮' },
        math_master_8: { name: 'Math Whiz (8th)', desc: 'Complete all Grade 8 math units', icon: '🧮' },
        math_master_9: { name: 'Algebra Ace', desc: 'Complete all Grade 9 math units', icon: '🧮' },
        math_master_10: { name: 'Geometry Guru', desc: 'Complete all Grade 10 math units', icon: '🧮' },
        math_master_11: { name: 'Trig Titan', desc: 'Complete all Grade 11 math units', icon: '🧮' },
        math_master_12: { name: 'Pre-Calc Pro', desc: 'Complete all Grade 12 math units', icon: '🧮' },
        science_explorer: { name: 'Science Explorer', desc: 'Complete a science unit', icon: '🔬' },
        science_master_9: { name: 'Biology Boss', desc: 'Complete all Grade 9 science units', icon: '🔬' },
        science_master_10: { name: 'Chemistry Champion', desc: 'Complete all Grade 10 science units', icon: '🔬' },
        science_master_11: { name: 'Physics Phenom', desc: 'Complete all Grade 11 science units', icon: '🔬' },
        science_master_12: { name: 'Earth Expert', desc: 'Complete all Grade 12 science units', icon: '🔬' },
        ela_reader: { name: 'Avid Reader', desc: 'Complete an ELA unit', icon: '📖' },
        ela_master_9: { name: 'World Lit Scholar', desc: 'Complete all Grade 9 ELA units', icon: '📖' },
        ela_master_10: { name: 'American Lit Scholar', desc: 'Complete all Grade 10 ELA units', icon: '📖' },
        ela_master_11: { name: 'British Lit Scholar', desc: 'Complete all Grade 11 ELA units', icon: '📖' },
        ela_master_12: { name: 'College-Ready Writer', desc: 'Complete all Grade 12 ELA units', icon: '📖' },
        social_historian: { name: 'History Buff', desc: 'Complete a social studies unit', icon: '🗺️' },
        social_master_9: { name: 'World History I Scholar', desc: 'Complete all Grade 9 social studies units', icon: '🗺️' },
        social_master_10: { name: 'World History II Scholar', desc: 'Complete all Grade 10 social studies units', icon: '🗺️' },
        social_master_11: { name: 'US History Expert', desc: 'Complete all Grade 11 social studies units', icon: '🗺️' },
        social_master_12: { name: 'Civics & Econ Pro', desc: 'Complete all Grade 12 social studies units', icon: '🗺️' },

        // Streak badges
        streak_3: { name: 'Getting Started', desc: '3-day learning streak', icon: '🔥' },
        streak_7: { name: 'Week Warrior', desc: '7-day learning streak', icon: '🔥' },
        streak_14: { name: 'Fortnight Force', desc: '14-day learning streak', icon: '🔥' },
        streak_30: { name: 'Monthly Master', desc: '30-day learning streak', icon: '🔥' },

        // Performance
        perfect_score: { name: 'Perfect Score', desc: 'Get 100% on a quiz', icon: '💯' },
        speed_demon: { name: 'Speed Demon', desc: 'Complete a quiz in under 2 minutes', icon: '⚡' },
        ten_lessons: { name: 'Lesson Lover', desc: 'Complete 10 lessons', icon: '📝' },
        fifty_lessons: { name: 'Knowledge Seeker', desc: 'Complete 50 lessons', icon: '🎓' },
        hundred_lessons: { name: 'Scholar', desc: 'Complete 100 lessons', icon: '🏛️' },

        // Exploration
        all_subjects: { name: 'Well-Rounded', desc: 'Try all 4 subjects', icon: '🌟' },
        tutor_user: { name: 'Help Seeker', desc: 'Use the AI tutor', icon: '🤝' },
        first_quiz: { name: 'Quiz Taker', desc: 'Complete your first quiz', icon: '📝' },
        daily_challenger: { name: 'Challenge Accepted', desc: 'Complete a daily challenge', icon: '⚡' },
    },

    /** Show XP gain animation */
    showXpGain(amount) {
        const toast = document.createElement('div');
        toast.className = 'xp-popup';
        toast.textContent = `+${amount} XP`;
        document.body.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('show'));
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 500);
        }, 2000);
    },

    /** Show badge earned animation */
    showBadgeEarned(badgeId) {
        const badge = this.badges[badgeId];
        if (!badge) return;

        this.fireConfetti();

        const overlay = document.createElement('div');
        overlay.className = 'badge-overlay';
        overlay.innerHTML = `
            <div class="badge-earned-card">
                <div class="badge-earned-icon">${badge.icon}</div>
                <h2>Badge Earned!</h2>
                <h3>${badge.name}</h3>
                <p>${badge.desc}</p>
                <button class="btn btn-primary" onclick="this.parentElement.parentElement.remove()">Awesome!</button>
            </div>
        `;
        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('show'));
    },

    /** Fire confetti animation */
    fireConfetti() {
        const canvas = document.getElementById('confetti-canvas');
        if (!canvas) return;

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        canvas.style.display = 'block';

        const ctx = canvas.getContext('2d');
        const pieces = [];
        const colors = ['#4A90D9', '#2ECC71', '#F39C12', '#9B59B6', '#E74C3C', '#1ABC9C'];

        for (let i = 0; i < 100; i++) {
            pieces.push({
                x: Math.random() * canvas.width,
                y: -10 - Math.random() * 100,
                w: 6 + Math.random() * 6,
                h: 4 + Math.random() * 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                vy: 2 + Math.random() * 3,
                vx: -1 + Math.random() * 2,
                rot: Math.random() * Math.PI * 2,
                vr: -0.1 + Math.random() * 0.2,
            });
        }

        let frame = 0;
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let alive = false;
            pieces.forEach(p => {
                if (p.y < canvas.height + 20) {
                    alive = true;
                    p.y += p.vy;
                    p.x += p.vx;
                    p.rot += p.vr;
                    p.vy += 0.05;
                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate(p.rot);
                    ctx.fillStyle = p.color;
                    ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
                    ctx.restore();
                }
            });
            frame++;
            if (alive && frame < 200) {
                requestAnimationFrame(animate);
            } else {
                canvas.style.display = 'none';
            }
        };
        animate();
    },

    /** Render badges page */
    async renderBadges(container) {
        try {
            const data = await App.api('/api/progress/badges');
            const earned = new Set((data.earned || []).map(b => b.badge_id));

            container.innerHTML = `
                <div class="page-container badges-page">
                    <h1>🏆 Badges</h1>
                    <p>Earn badges by completing lessons, quizzes, and challenges!</p>
                    <div class="badges-grid">
                        ${Object.entries(this.badges).map(([id, badge]) => `
                            <div class="badge-card ${earned.has(id) ? 'earned' : 'locked'}">
                                <div class="badge-icon">${earned.has(id) ? badge.icon : '🔒'}</div>
                                <div class="badge-name">${badge.name}</div>
                                <div class="badge-desc">${badge.desc}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (err) {
            container.innerHTML = `<div class="page-container"><p class="error-msg">Error: ${err.message}</p></div>`;
        }
    }
};
