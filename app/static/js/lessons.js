/**
 * LearnQuest - Lesson Viewer
 */

const Lessons = {
    currentLesson: null,
    currentProblemIndex: 0,
    problemResults: [],

    /** Render units for a subject+grade */
    async renderUnits(container, subject, grade) {
        try {
            const data = await App.api(`/api/curriculum/${subject}/${grade}`);
            const units = data.units || [];
            const subjectNames = { math: 'Mathematics', science: 'Science', ela: 'English Language Arts', social_studies: 'Social Studies' };
            const subjectColors = { math: 'math', science: 'science', ela: 'ela', social_studies: 'social' };
            const gradeLabel = grade === 0 || grade === '0' ? 'Kindergarten' : `Grade ${grade}`;

            container.innerHTML = `
                <div class="page-container units-page">
                    <button class="btn btn-secondary" onclick="App.navigate('home')">← Back</button>
                    <h1>${subjectNames[subject] || subject} - ${gradeLabel}</h1>
                    <div class="units-list">
                        ${units.map((unit, idx) => `
                            <div class="unit-card ${subjectColors[subject] || ''}">
                                <div class="unit-header">
                                    <span class="unit-number">Unit ${idx + 1}</span>
                                    <h2>${App.escapeHtml(unit.title)}</h2>
                                    <p>${App.escapeHtml(unit.description || '')}</p>
                                </div>
                                <div class="lessons-list">
                                    ${(unit.lessons || []).map((lesson, lIdx) => `
                                        <div class="lesson-item" onclick="App.navigate('lesson', {lessonId:'${lesson.id}', subject:'${subject}', grade:${grade}})">
                                            <span class="lesson-number">${lIdx + 1}</span>
                                            <span class="lesson-title">${App.escapeHtml(lesson.title)}</span>
                                            <span class="lesson-xp">+${lesson.xp_reward || 20} XP</span>
                                        </div>
                                    `).join('')}
                                </div>
                                ${unit.unit_quiz ? `
                                    <div class="unit-quiz-btn">
                                        <button class="btn btn-primary" onclick="App.navigate('quiz', {unitId:'${unit.id}', subject:'${subject}', grade:${grade}})">
                                            📝 Unit Quiz (+${unit.unit_quiz.xp_reward || 50} XP)
                                        </button>
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (err) {
            container.innerHTML = `
                <div class="page-container">
                    <button class="btn btn-secondary" onclick="App.navigate('home')">← Back</button>
                    <p class="error-msg">Error loading content: ${err.message}</p>
                </div>
            `;
        }
    },

    /** Render a single lesson */
    async renderLesson(container, lessonId, subject, grade) {
        try {
            const data = await App.api(`/api/lesson/${lessonId}?subject=${subject}&grade=${grade}`);
            this.currentLesson = data;
            this.currentProblemIndex = 0;
            this.problemResults = [];

            const lesson = data;
            const content = lesson.content || {};

            // Set tutor context
            Tutor.setContext(lessonId, subject, grade);

            // Check bookmark status
            let isBookmarked = false;
            try {
                const bm = await App.api(`/api/bookmarks/check/${lessonId}`);
                isBookmarked = bm.bookmarked;
            } catch (e) { /* ignore */ }

            container.innerHTML = `
                <div class="page-container lesson-page">
                    <button class="btn btn-secondary" onclick="App.navigate('units', {subject:'${subject}', grade:${grade}})">← Back to Units</button>

                    <div class="lesson-toolbar">
                        <button class="bookmark-btn ${isBookmarked ? 'active' : ''}" id="bookmark-btn" onclick="Lessons.toggleBookmark('${lessonId}', '${subject}', ${grade}, '${App.escapeHtml(lesson.title).replace(/'/g, "\\'")}')">
                            ${isBookmarked ? '&#9733;' : '&#9734;'} Bookmark
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="Lessons.toggleNotes('${lessonId}', '${subject}', ${grade}, '${App.escapeHtml(lesson.title).replace(/'/g, "\\'")}')">Take Notes</button>
                        <button class="btn btn-secondary btn-sm" onclick="window.open('/api/worksheet/${lessonId}?subject=${subject}&grade=${grade}', '_blank')">Print Worksheet</button>
                    </div>

                    <div class="lesson-content">
                        <h1>${App.escapeHtml(lesson.title)}</h1>

                        <div class="lesson-explanation">
                            <h2>📖 Learn</h2>
                            <div class="explanation-text">${this.formatText(content.explanation || '')}</div>

                            ${content.key_vocabulary ? `
                                <div class="vocabulary-box">
                                    <h3>📝 Key Words</h3>
                                    <div class="vocab-list">
                                        ${content.key_vocabulary.map(v => `<span class="vocab-tag">${App.escapeHtml(v)}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            ${content.examples ? `
                                <div class="examples-box">
                                    <h3>💡 Examples</h3>
                                    ${content.examples.map(ex => `
                                        <div class="example-item">
                                            <div class="example-problem">${App.escapeHtml(ex.problem || '')}</div>
                                            ${ex.visual ? `<div class="example-visual">${App.escapeHtml(ex.visual)}</div>` : ''}
                                            <div class="example-answer">Answer: ${App.escapeHtml(String(ex.answer || ''))}</div>
                                            <div class="example-explain">${App.escapeHtml(ex.explanation || '')}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}

                            ${content.real_world ? `
                                <div class="real-world-box">
                                    <h3>🌍 Real World Connection</h3>
                                    <p>${App.escapeHtml(content.real_world)}</p>
                                </div>
                            ` : ''}
                        </div>

                        <div class="lesson-practice" id="practice-area">
                            <h2>✏️ Practice</h2>
                            <div class="practice-progress">
                                <span id="practice-progress-text">Problem 1 of ${(lesson.practice_problems || []).length}</span>
                                <div class="practice-bar">
                                    <div class="practice-bar-fill" id="practice-bar-fill" style="width:0%"></div>
                                </div>
                            </div>
                            <div id="problem-container">
                                ${(lesson.practice_problems && lesson.practice_problems.length > 0) ?
                                    this.renderProblem(lesson.practice_problems[0], 0, subject) :
                                    '<p>No practice problems available for this lesson.</p>'
                                }
                            </div>
                        </div>

                        <div class="lesson-actions">
                            <button class="btn btn-accent" onclick="Tutor.toggle()">🤔 I need help!</button>
                        </div>
                    </div>
                </div>
            `;
        } catch (err) {
            container.innerHTML = `
                <div class="page-container">
                    <button class="btn btn-secondary" onclick="App.navigate('units', {subject:'${subject}', grade:${grade}})">← Back</button>
                    <p class="error-msg">Error loading lesson: ${err.message}</p>
                </div>
            `;
        }
    },

    /** Render a single practice problem */
    renderProblem(problem, index, subject) {
        if (!problem) return '<p>All done!</p>';

        let html = `<div class="problem-card" data-index="${index}">`;
        html += `<div class="problem-question">${App.escapeHtml(problem.question)}</div>`;

        if (problem.type === 'multiple_choice') {
            html += `<div class="mc-options">
                ${(problem.options || []).map((opt, i) => `
                    <button class="mc-option" onclick="Lessons.submitAnswer(${index}, ${i}, '${subject}')" data-idx="${i}">
                        <span class="mc-letter">${String.fromCharCode(65 + i)}</span>
                        ${App.escapeHtml(String(opt))}
                    </button>
                `).join('')}
            </div>`;
        } else if (problem.type === 'true_false') {
            html += `<div class="mc-options">
                <button class="mc-option" onclick="Lessons.submitAnswer(${index}, 'true', '${subject}')">
                    <span class="mc-letter">T</span> True
                </button>
                <button class="mc-option" onclick="Lessons.submitAnswer(${index}, 'false', '${subject}')">
                    <span class="mc-letter">F</span> False
                </button>
            </div>`;
        } else {
            // fill_in, word_problem, etc.
            html += `<div class="fill-in-area">
                <input type="text" id="answer-input-${index}" class="answer-input" placeholder="Type your answer..." onkeypress="if(event.key==='Enter')Lessons.submitTextAnswer(${index}, '${subject}')">
                <button class="btn btn-primary" onclick="Lessons.submitTextAnswer(${index}, '${subject}')">Check Answer</button>
            </div>`;
        }

        html += `<div class="problem-feedback hidden" id="feedback-${index}"></div>`;
        html += `<div class="problem-hint" id="hint-${index}">
            <button class="btn btn-hint" onclick="Lessons.showHint(${index})">💡 Show Hint</button>
            <div class="hint-text hidden" id="hint-text-${index}"></div>
        </div>`;
        html += `</div>`;
        return html;
    },

    /** Submit multiple choice answer */
    async submitAnswer(problemIdx, answer, subject) {
        const problems = this.currentLesson.practice_problems;
        const problem = problems[problemIdx];
        if (!problem) return;

        let isCorrect;
        if (problem.type === 'multiple_choice') {
            isCorrect = answer === problem.correct;
        } else if (problem.type === 'true_false') {
            isCorrect = String(answer).toLowerCase() === String(problem.answer).toLowerCase();
        }

        // If math subject, also verify with backend
        if (subject === 'math' && problem.answer !== undefined) {
            try {
                const check = await App.api('/api/math/check', {
                    method: 'POST',
                    body: {
                        student_answer: String(problem.options ? problem.options[answer] : answer),
                        correct_answer: String(problem.answer || problem.options[problem.correct])
                    }
                });
                isCorrect = check.correct;
            } catch (e) { /* fall back to local check */ }
        }

        this.showFeedback(problemIdx, isCorrect, problem);

        // Disable options
        const card = document.querySelector(`.problem-card[data-index="${problemIdx}"]`);
        if (card) {
            card.querySelectorAll('.mc-option').forEach(btn => btn.disabled = true);
            if (problem.type === 'multiple_choice') {
                const correct = card.querySelectorAll('.mc-option')[problem.correct];
                if (correct) correct.classList.add('correct');
                if (!isCorrect) {
                    const selected = card.querySelectorAll('.mc-option')[answer];
                    if (selected) selected.classList.add('wrong');
                }
            }
        }

        this.problemResults.push(isCorrect);
        this.advanceAfterDelay(problemIdx, subject);
    },

    /** Submit text answer */
    async submitTextAnswer(problemIdx, subject) {
        const problems = this.currentLesson.practice_problems;
        const problem = problems[problemIdx];
        if (!problem) return;

        const input = document.getElementById(`answer-input-${problemIdx}`);
        const answer = input.value.trim();
        if (!answer) return;

        let isCorrect;

        // For math, use backend validation
        if (subject === 'math') {
            try {
                const check = await App.api('/api/math/check', {
                    method: 'POST',
                    body: {
                        student_answer: answer,
                        correct_answer: String(problem.answer)
                    }
                });
                isCorrect = check.correct;
            } catch (e) {
                isCorrect = answer.toLowerCase() === String(problem.answer).toLowerCase();
            }
        } else {
            // Simple string comparison for non-math
            isCorrect = answer.toLowerCase().replace(/\s+/g, ' ') ===
                        String(problem.answer).toLowerCase().replace(/\s+/g, ' ');
        }

        input.disabled = true;
        this.showFeedback(problemIdx, isCorrect, problem);
        this.problemResults.push(isCorrect);
        this.advanceAfterDelay(problemIdx, subject);
    },

    /** Show feedback for a problem */
    showFeedback(problemIdx, isCorrect, problem) {
        const el = document.getElementById(`feedback-${problemIdx}`);
        if (!el) return;
        el.classList.remove('hidden');
        if (isCorrect) {
            el.innerHTML = `<div class="feedback-correct">Correct! Great job!</div>`;
        } else {
            const correctAnswer = problem.type === 'multiple_choice' ?
                problem.options[problem.correct] : problem.answer;
            el.innerHTML = `<div class="feedback-wrong">Not quite. The answer is: <strong>${App.escapeHtml(String(correctAnswer))}</strong></div>`;
            // Show proactive tutor tip
            if (typeof Tutor !== 'undefined' && Tutor.showWrongAnswerTip) {
                Tutor.showWrongAnswerTip();
            }
        }
    },

    /** Advance to next problem after a delay */
    advanceAfterDelay(problemIdx, subject) {
        const problems = this.currentLesson.practice_problems;
        setTimeout(() => {
            const nextIdx = problemIdx + 1;
            if (nextIdx < problems.length) {
                this.currentProblemIndex = nextIdx;
                const container = document.getElementById('problem-container');
                container.innerHTML = this.renderProblem(problems[nextIdx], nextIdx, subject);
                document.getElementById('practice-progress-text').textContent =
                    `Problem ${nextIdx + 1} of ${problems.length}`;
                const pct = (nextIdx / problems.length) * 100;
                document.getElementById('practice-bar-fill').style.width = pct + '%';
            } else {
                this.completePractice(subject);
            }
        }, 1500);
    },

    /** Complete practice section */
    async completePractice(subject) {
        const correct = this.problemResults.filter(r => r).length;
        const total = this.problemResults.length;
        const score = total > 0 ? Math.round((correct / total) * 100) : 0;
        const lesson = this.currentLesson;

        document.getElementById('practice-bar-fill').style.width = '100%';
        document.getElementById('problem-container').innerHTML = `
            <div class="practice-complete">
                <h2>${score >= 70 ? '🎉 Great Job!' : '📚 Keep Practicing!'}</h2>
                <div class="score-display">
                    <div class="score-circle ${score >= 70 ? 'pass' : 'fail'}">
                        <span class="score-number">${score}%</span>
                    </div>
                    <p>${correct} out of ${total} correct</p>
                </div>
                ${score >= 70 ? `<p class="xp-earned">+${lesson.xp_reward || 20} XP earned!</p>` : ''}
                <button class="btn btn-primary" onclick="App.navigate('units', {subject:'${subject}', grade:${App.state.user.grade}})">Continue</button>
            </div>
        `;

        // Report completion to server
        try {
            await App.api(`/api/lesson/${lesson.id}/complete`, {
                method: 'POST',
                body: { subject, grade: App.state.user.grade, score }
            });
            await App.refreshUser();
            if (score >= 70) {
                Gamification.showXpGain(lesson.xp_reward || 20);
            }
        } catch (e) { /* ignore */ }
    },

    /** Show hint for a problem */
    async showHint(problemIdx) {
        const problems = this.currentLesson.practice_problems;
        const problem = problems[problemIdx];
        const hintText = document.getElementById(`hint-text-${problemIdx}`);
        if (!hintText) return;

        if (problem.hint) {
            hintText.textContent = problem.hint;
            hintText.classList.remove('hidden');
        } else {
            hintText.textContent = 'Think about what the question is asking step by step.';
            hintText.classList.remove('hidden');
        }
    },

    /** Toggle bookmark for current lesson */
    async toggleBookmark(lessonId, subject, grade, title) {
        try {
            const data = await App.api('/api/bookmarks/toggle', {
                method: 'POST',
                body: { lesson_id: lessonId, lesson_title: title, subject, grade }
            });
            const btn = document.getElementById('bookmark-btn');
            if (btn) {
                btn.classList.toggle('active', data.bookmarked);
                btn.innerHTML = (data.bookmarked ? '&#9733;' : '&#9734;') + ' Bookmark';
            }
            App.showToast(data.bookmarked ? 'Bookmarked!' : 'Bookmark removed', 'success');
        } catch (e) {
            App.showToast('Error toggling bookmark', 'error');
        }
    },

    /** Toggle notes panel */
    _notesOpen: false,
    async toggleNotes(lessonId, subject, grade, title) {
        const existing = document.getElementById('notes-panel');
        if (existing) {
            existing.remove();
            this._notesOpen = false;
            return;
        }

        this._notesOpen = true;
        let existingNote = '';
        try {
            const data = await App.api(`/api/notes?lesson_id=${lessonId}`);
            if (data.notes && data.notes.length > 0) {
                existingNote = data.notes[0].content;
            }
        } catch (e) { /* ignore */ }

        const panel = document.createElement('div');
        panel.className = 'notes-panel';
        panel.id = 'notes-panel';
        panel.innerHTML = `
            <h3>Notes</h3>
            <textarea class="notes-textarea" id="notes-textarea" placeholder="Write your notes here...">${App.escapeHtml(existingNote)}</textarea>
            <div style="margin-top:0.5rem">
                <button class="btn btn-primary btn-sm" onclick="Lessons.saveNote('${lessonId}', '${subject}', ${grade}, '${title.replace(/'/g, "\\'")}')">Save Note</button>
                <button class="btn btn-secondary btn-sm" onclick="document.getElementById('notes-panel').remove()">Close</button>
            </div>
        `;

        const lessonContent = document.querySelector('.lesson-content');
        if (lessonContent) {
            lessonContent.parentElement.insertBefore(panel, lessonContent.nextSibling);
        }
    },

    async saveNote(lessonId, subject, grade, title) {
        const content = document.getElementById('notes-textarea')?.value?.trim();
        if (!content) {
            App.showToast('Note is empty', 'error');
            return;
        }
        try {
            await App.api('/api/notes', {
                method: 'POST',
                body: { lesson_id: lessonId, lesson_title: title, subject, grade, content }
            });
            App.showToast('Note saved!', 'success');
        } catch (e) {
            App.showToast('Error saving note', 'error');
        }
    },

    /** Format text with basic markdown */
    formatText(text) {
        return App.escapeHtml(text)
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>');
    }
};
