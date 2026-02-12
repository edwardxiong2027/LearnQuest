/**
 * LearnQuest - Quiz Engine
 */

const Quiz = {
    currentQuiz: null,
    currentQuestionIndex: 0,
    answers: [],
    startTime: null,
    timerInterval: null,

    /** Render quiz page */
    async renderQuiz(container, unitId, subject, grade) {
        try {
            const data = await App.api(`/api/quiz/${unitId}?subject=${subject}&grade=${grade}`);
            this.currentQuiz = data;
            this.currentQuestionIndex = 0;
            this.answers = [];
            this.startTime = Date.now();

            container.innerHTML = `
                <div class="page-container quiz-page">
                    <div class="quiz-header">
                        <button class="btn btn-secondary" onclick="Quiz.confirmExit('${subject}', ${grade})">← Exit Quiz</button>
                        <h1>📝 ${App.escapeHtml(data.title || 'Unit Quiz')}</h1>
                        <div class="quiz-info">
                            <span class="quiz-progress" id="quiz-progress">Question 1 of ${data.questions.length}</span>
                            <span class="quiz-timer" id="quiz-timer"></span>
                        </div>
                    </div>
                    <div class="quiz-progress-bar">
                        <div class="quiz-progress-fill" id="quiz-progress-fill" style="width:0%"></div>
                    </div>
                    <div id="quiz-question-area">
                        ${this.renderQuestion(data.questions[0], 0, subject)}
                    </div>
                </div>
            `;

            // Start timer if enabled
            this.startTimer();
        } catch (err) {
            container.innerHTML = `
                <div class="page-container">
                    <button class="btn btn-secondary" onclick="App.navigate('units', {subject:'${subject}', grade:${grade}})">← Back</button>
                    <p class="error-msg">Error loading quiz: ${err.message}</p>
                </div>
            `;
        }
    },

    /** Render a single question */
    renderQuestion(question, index, subject) {
        if (!question) return '';

        let html = `<div class="quiz-question-card" data-index="${index}">`;
        html += `<div class="quiz-question-text">${App.escapeHtml(question.question)}</div>`;

        if (question.type === 'multiple_choice') {
            html += `<div class="mc-options">
                ${(question.options || []).map((opt, i) => `
                    <button class="mc-option" onclick="Quiz.selectAnswer(${index}, ${i}, '${subject}')">
                        <span class="mc-letter">${String.fromCharCode(65 + i)}</span>
                        ${App.escapeHtml(String(opt))}
                    </button>
                `).join('')}
            </div>`;
        } else if (question.type === 'true_false') {
            html += `<div class="mc-options">
                <button class="mc-option" onclick="Quiz.selectAnswer(${index}, 'true', '${subject}')">
                    <span class="mc-letter">T</span> True
                </button>
                <button class="mc-option" onclick="Quiz.selectAnswer(${index}, 'false', '${subject}')">
                    <span class="mc-letter">F</span> False
                </button>
            </div>`;
        } else if (question.type === 'matching') {
            html += `<div class="matching-area">
                ${(question.pairs || []).map((pair, i) => `
                    <div class="matching-row">
                        <span class="matching-left">${App.escapeHtml(pair.left || pair[0])}</span>
                        <select class="matching-select" id="match-${index}-${i}">
                            <option value="">Select...</option>
                            ${(question.right_options || question.pairs.map(p => p.right || p[1])).map((opt, j) => `
                                <option value="${j}">${App.escapeHtml(opt)}</option>
                            `).join('')}
                        </select>
                    </div>
                `).join('')}
                <button class="btn btn-primary" onclick="Quiz.submitMatching(${index}, '${subject}')">Submit</button>
            </div>`;
        } else {
            // fill_in, word_problem
            html += `<div class="fill-in-area">
                <input type="text" id="quiz-answer-${index}" class="answer-input" placeholder="Type your answer..." onkeypress="if(event.key==='Enter')Quiz.submitTextAnswer(${index}, '${subject}')">
                <button class="btn btn-primary" onclick="Quiz.submitTextAnswer(${index}, '${subject}')">Submit</button>
            </div>`;
        }

        html += `<div class="quiz-feedback hidden" id="quiz-feedback-${index}"></div>`;
        html += `</div>`;
        return html;
    },

    /** Handle MC answer selection */
    async selectAnswer(questionIdx, answer, subject) {
        const question = this.currentQuiz.questions[questionIdx];
        let isCorrect;

        if (question.type === 'multiple_choice') {
            isCorrect = answer === question.correct;
        } else if (question.type === 'true_false') {
            isCorrect = String(answer).toLowerCase() === String(question.answer).toLowerCase();
        }

        // Verify math with backend
        if (subject === 'math' && question.answer !== undefined) {
            try {
                const selectedAnswer = question.options ? question.options[answer] : answer;
                const correctAnswer = question.answer || (question.options ? question.options[question.correct] : '');
                const check = await App.api('/api/math/check', {
                    method: 'POST',
                    body: { student_answer: String(selectedAnswer), correct_answer: String(correctAnswer) }
                });
                isCorrect = check.correct;
            } catch (e) { /* fall back */ }
        }

        this.answers.push({ questionIdx, answer, correct: isCorrect });
        this.showQuizFeedback(questionIdx, isCorrect, question);

        // Highlight correct/wrong
        const card = document.querySelector(`.quiz-question-card[data-index="${questionIdx}"]`);
        if (card) {
            card.querySelectorAll('.mc-option').forEach(btn => btn.disabled = true);
            if (question.type === 'multiple_choice') {
                card.querySelectorAll('.mc-option')[question.correct]?.classList.add('correct');
                if (!isCorrect) {
                    card.querySelectorAll('.mc-option')[answer]?.classList.add('wrong');
                }
            }
        }

        this.advanceQuestion(subject);
    },

    /** Submit text answer for quiz */
    async submitTextAnswer(questionIdx, subject) {
        const question = this.currentQuiz.questions[questionIdx];
        const input = document.getElementById(`quiz-answer-${questionIdx}`);
        const answer = input.value.trim();
        if (!answer) return;

        let isCorrect;
        if (subject === 'math') {
            try {
                const check = await App.api('/api/math/check', {
                    method: 'POST',
                    body: { student_answer: answer, correct_answer: String(question.answer) }
                });
                isCorrect = check.correct;
            } catch (e) {
                isCorrect = answer.toLowerCase() === String(question.answer).toLowerCase();
            }
        } else {
            isCorrect = answer.toLowerCase().replace(/\s+/g, ' ') ===
                        String(question.answer).toLowerCase().replace(/\s+/g, ' ');
        }

        input.disabled = true;
        this.answers.push({ questionIdx, answer, correct: isCorrect });
        this.showQuizFeedback(questionIdx, isCorrect, question);
        this.advanceQuestion(subject);
    },

    /** Submit matching answers */
    submitMatching(questionIdx, subject) {
        const question = this.currentQuiz.questions[questionIdx];
        const pairs = question.pairs || [];
        let correct = 0;
        pairs.forEach((pair, i) => {
            const sel = document.getElementById(`match-${questionIdx}-${i}`);
            if (sel && parseInt(sel.value) === i) correct++;
        });
        const isCorrect = correct === pairs.length;
        this.answers.push({ questionIdx, correct: isCorrect });
        this.showQuizFeedback(questionIdx, isCorrect, question);
        this.advanceQuestion(subject);
    },

    /** Show feedback for quiz question */
    showQuizFeedback(questionIdx, isCorrect, question) {
        const el = document.getElementById(`quiz-feedback-${questionIdx}`);
        if (!el) return;
        el.classList.remove('hidden');
        if (isCorrect) {
            el.innerHTML = `<div class="feedback-correct">✅ Correct!</div>`;
        } else {
            const ans = question.type === 'multiple_choice' ?
                question.options[question.correct] : question.answer;
            el.innerHTML = `<div class="feedback-wrong">❌ The correct answer is: <strong>${App.escapeHtml(String(ans))}</strong></div>`;
        }
    },

    /** Advance to next question */
    advanceQuestion(subject) {
        const questions = this.currentQuiz.questions;
        setTimeout(() => {
            const nextIdx = this.currentQuestionIndex + 1;
            if (nextIdx < questions.length) {
                this.currentQuestionIndex = nextIdx;
                const area = document.getElementById('quiz-question-area');
                area.innerHTML = this.renderQuestion(questions[nextIdx], nextIdx, subject);
                document.getElementById('quiz-progress').textContent =
                    `Question ${nextIdx + 1} of ${questions.length}`;
                document.getElementById('quiz-progress-fill').style.width =
                    ((nextIdx / questions.length) * 100) + '%';
            } else {
                this.finishQuiz(subject);
            }
        }, 1500);
    },

    /** Finish quiz and show results */
    async finishQuiz(subject) {
        if (this.timerInterval) clearInterval(this.timerInterval);

        const correct = this.answers.filter(a => a.correct).length;
        const total = this.answers.length;
        const score = total > 0 ? Math.round((correct / total) * 100) : 0;
        const timeSpent = Math.round((Date.now() - this.startTime) / 1000);
        const quiz = this.currentQuiz;
        const passing = quiz.passing_score || 70;
        const passed = score >= passing;

        document.getElementById('quiz-progress-fill').style.width = '100%';
        document.getElementById('quiz-question-area').innerHTML = `
            <div class="quiz-results">
                <h2>${passed ? '🎉 You Passed!' : '📚 Keep Trying!'}</h2>
                <div class="score-circle ${passed ? 'pass' : 'fail'}">
                    <span class="score-number">${score}%</span>
                </div>
                <p>${correct} out of ${total} correct</p>
                <p class="quiz-time">Time: ${Math.floor(timeSpent / 60)}m ${timeSpent % 60}s</p>
                ${passed ? `<p class="xp-earned">+${quiz.xp_reward || 50} XP earned!</p>` : ''}
                ${!passed ? `<p>You need ${passing}% to pass. Review the lessons and try again!</p>` : ''}
                <div class="quiz-result-actions">
                    <button class="btn btn-primary" onclick="App.navigate('units', {subject:'${subject}', grade:${App.state.user.grade}})">Continue</button>
                    ${!passed ? `<button class="btn btn-secondary" onclick="App.navigate('quiz', {unitId:'${quiz.unit_id}', subject:'${subject}', grade:${App.state.user.grade}})">Retry</button>` : ''}
                </div>
            </div>
        `;

        // Submit results
        try {
            await App.api('/api/quiz/submit', {
                method: 'POST',
                body: {
                    quiz_id: quiz.unit_id || quiz.id,
                    subject,
                    grade: App.state.user.grade,
                    score,
                    total_questions: total,
                    correct_answers: correct,
                    time_spent_seconds: timeSpent,
                    answers: this.answers
                }
            });
            await App.refreshUser();
            if (passed) {
                Gamification.showXpGain(quiz.xp_reward || 50);
                if (score === 100) {
                    Gamification.showXpGain(25); // bonus
                }
            }
        } catch (e) { /* ignore */ }
    },

    /** Start timer */
    startTimer() {
        const timerEl = document.getElementById('quiz-timer');
        if (!timerEl) return;
        const elapsed = () => {
            const secs = Math.floor((Date.now() - this.startTime) / 1000);
            const m = Math.floor(secs / 60);
            const s = secs % 60;
            timerEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
        };
        elapsed();
        this.timerInterval = setInterval(elapsed, 1000);
    },

    /** Confirm exit quiz */
    confirmExit(subject, grade) {
        if (this.answers.length > 0) {
            if (!confirm('Are you sure you want to exit? Your progress will be lost.')) return;
        }
        if (this.timerInterval) clearInterval(this.timerInterval);
        App.navigate('units', { subject, grade });
    }
};
