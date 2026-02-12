/**
 * LearnQuest - AI Studio: Generate lessons, quizzes, flashcards, practice
 * With topic presets, formatted output, and math rendering.
 */

const Generate = {
    currentType: 'lesson',
    topicPresets: [],

    renderStudio(container) {
        const user = App.state.user;
        if (!user) return App.navigate('login');
        const grade = user.grade || 3;

        container.innerHTML = `
            <div class="page-container studio-page">
                <h1 class="studio-title">AI Studio</h1>
                <p class="studio-subtitle">Create custom learning content on any topic!</p>

                <div class="studio-controls">
                    <div class="studio-controls-row">
                        <div class="form-group">
                            <label>Subject</label>
                            <select id="studio-subject" onchange="Generate.onSubjectGradeChange()">
                                <option value="math">Math</option>
                                <option value="science">Science</option>
                                <option value="ela">English Language Arts</option>
                                <option value="social_studies">Social Studies</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Grade</label>
                            <select id="studio-grade" onchange="Generate.onSubjectGradeChange()">
                                <option value="0" ${grade === 0 ? 'selected' : ''}>Kindergarten</option>
                                ${[1,2,3,4,5,6,7,8,9,10,11,12].map(g => `<option value="${g}" ${grade === g ? 'selected' : ''}>Grade ${g}</option>`).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Topic</label>
                        <div class="topic-input-wrap">
                            <select id="studio-topic-preset" onchange="Generate.onPresetChange()">
                                <option value="">-- Select a topic --</option>
                            </select>
                            <input type="text" id="studio-topic" placeholder="Or type your own topic..." class="topic-custom-input">
                        </div>
                    </div>
                </div>

                <div class="studio-type-selector">
                    <button class="studio-type-btn active" onclick="Generate.setType('lesson')" data-type="lesson">
                        <span class="studio-type-icon">📖</span> Lesson
                    </button>
                    <button class="studio-type-btn" onclick="Generate.setType('quiz')" data-type="quiz">
                        <span class="studio-type-icon">✅</span> Quiz
                    </button>
                    <button class="studio-type-btn" onclick="Generate.setType('flashcards')" data-type="flashcards">
                        <span class="studio-type-icon">🃏</span> Flashcards
                    </button>
                    <button class="studio-type-btn" onclick="Generate.setType('practice')" data-type="practice">
                        <span class="studio-type-icon">✏️</span> Practice
                    </button>
                </div>

                <button class="btn btn-primary btn-large studio-generate-btn" onclick="Generate.generate()">
                    Generate Content
                </button>

                <div id="studio-output"></div>

                <div class="studio-saved-section">
                    <h2>My Saved Content</h2>
                    <div id="studio-saved">Loading...</div>
                </div>
            </div>
        `;

        this.onSubjectGradeChange();
        this.loadSaved();
    },

    async onSubjectGradeChange() {
        const subject = document.getElementById('studio-subject').value;
        const grade = parseInt(document.getElementById('studio-grade').value);
        try {
            const data = await App.api(`/api/generate/topics?subject=${subject}&grade=${grade}`);
            this.topicPresets = data.topics || [];
        } catch (e) {
            this.topicPresets = [];
        }
        const preset = document.getElementById('studio-topic-preset');
        if (preset) {
            preset.innerHTML = '<option value="">-- Select a topic --</option>' +
                this.topicPresets.map(t => `<option value="${App.escapeHtml(t)}">${App.escapeHtml(t)}</option>`).join('');
        }
    },

    onPresetChange() {
        const preset = document.getElementById('studio-topic-preset').value;
        const input = document.getElementById('studio-topic');
        if (preset && input) {
            input.value = preset;
        }
    },

    setType(type) {
        this.currentType = type;
        document.querySelectorAll('.studio-type-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.type === type);
        });
    },

    async generate() {
        const subject = document.getElementById('studio-subject').value;
        const grade = parseInt(document.getElementById('studio-grade').value);
        const topic = document.getElementById('studio-topic').value.trim() ||
                      document.getElementById('studio-topic-preset').value;

        if (!topic) {
            App.showToast('Please select or enter a topic', 'error');
            return;
        }

        const output = document.getElementById('studio-output');
        output.innerHTML = `
            <div class="studio-loading">
                <div class="spinner"></div>
                <p>Creating your ${this.currentType}...</p>
                <p class="studio-loading-hint">This may take a few moments</p>
            </div>
        `;

        try {
            const body = { subject, grade, topic, count: this.currentType === 'flashcards' ? 8 : 5 };
            const data = await App.api(`/api/generate/${this.currentType}`, {
                method: 'POST',
                body
            });

            if (data.error) {
                App.showToast(data.error, 'error');
            }

            if (this.currentType === 'lesson') {
                this.renderLesson(output, data.content || data, subject);
            } else if (this.currentType === 'quiz') {
                this.renderQuizPreview(output, data.questions || [], subject);
            } else if (this.currentType === 'flashcards') {
                this.renderFlashcardPreview(output, data.flashcards || [], subject);
            } else if (this.currentType === 'practice') {
                this.renderPracticePreview(output, data.problems || [], subject);
            }

            if (data.cached) {
                App.showToast('Loaded from cache', 'info');
            }

            this.loadSaved();
        } catch (err) {
            output.innerHTML = `<div class="studio-result studio-error"><p>Error: ${App.escapeHtml(err.message)}</p><p>Make sure Ollama is running, or try a topic from the dropdown.</p></div>`;
        }
    },

    /** Format math expressions: convert common patterns to displayable format */
    formatMath(text) {
        if (!text) return '';
        let s = App.escapeHtml(String(text));
        // Fraction: a/b -> display as fraction
        s = s.replace(/(\d+)\s*\/\s*(\d+)/g, '<span class="math-frac"><span class="math-num">$1</span><span class="math-den">$2</span></span>');
        // Exponents: x^2 or x^{12}
        s = s.replace(/\^{?\s*(\d+)\s*}?/g, '<sup>$1</sup>');
        // Multiplication sign
        s = s.replace(/(\d)\s*[x×]\s*(\d)/g, '$1 &times; $2');
        // Division sign
        s = s.replace(/(\d)\s*÷\s*(\d)/g, '$1 &divide; $2');
        // Square root
        s = s.replace(/√\s*(\d+)/g, '&radic;$1');
        // Pi
        s = s.replace(/\bpi\b/gi, '&pi;');
        return s;
    },

    /** Render formatted text (with math for math subject, otherwise plain) */
    fmt(text, subject) {
        if (subject === 'math') {
            return this.formatMath(text);
        }
        return App.escapeHtml(String(text || '')).replace(/\n/g, '<br>');
    },

    renderLesson(container, content, subject) {
        if (!content || (!content.title && !content.explanation)) {
            container.innerHTML = '<div class="studio-result"><p>No lesson content generated. Try a different topic.</p></div>';
            return;
        }
        container.innerHTML = `
            <div class="studio-result studio-lesson">
                <div class="studio-result-header">
                    <h2>${this.fmt(content.title || 'Generated Lesson', subject)}</h2>
                    <span class="studio-result-badge">${subject}</span>
                </div>

                <div class="studio-section">
                    <div class="lesson-explanation">${(content.explanation || '').replace(/\n/g, '<br>')}</div>
                </div>

                ${content.key_vocabulary && content.key_vocabulary.length ? `
                    <div class="studio-section">
                        <h3>Key Vocabulary</h3>
                        <div class="vocab-tags">
                            ${content.key_vocabulary.map(v => `<span class="vocab-tag">${App.escapeHtml(v)}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}

                ${content.examples && content.examples.length ? `
                    <div class="studio-section">
                        <h3>Examples</h3>
                        <div class="examples-list">
                            ${content.examples.map((ex, i) => `
                                <div class="example-card">
                                    <div class="example-num">${i + 1}</div>
                                    <div class="example-body">
                                        <div class="example-problem">${this.fmt(ex.problem || '', subject)}</div>
                                        <div class="example-answer">= ${this.fmt(ex.answer || '', subject)}</div>
                                        ${ex.explanation ? `<div class="example-explain">${App.escapeHtml(ex.explanation)}</div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${content.real_world ? `
                    <div class="studio-section studio-real-world">
                        <h3>Real World Connection</h3>
                        <p>${App.escapeHtml(content.real_world)}</p>
                    </div>
                ` : ''}

                ${content.practice_problems && content.practice_problems.length ? `
                    <div class="studio-section">
                        <h3>Practice Problems (${content.practice_problems.length})</h3>
                        ${content.practice_problems.map((p, i) => `
                            <div class="problem-card">
                                <div class="problem-num">${i + 1}</div>
                                <div class="problem-body">
                                    <div class="problem-question">${this.fmt(p.question, subject)}</div>
                                    ${p.options ? `
                                        <div class="problem-options">
                                            ${p.options.map((o, j) => `
                                                <div class="problem-option ${j === p.correct ? 'correct' : ''}">${String.fromCharCode(65 + j)}. ${this.fmt(o, subject)}</div>
                                            `).join('')}
                                        </div>
                                    ` : `<div class="problem-answer-reveal" onclick="this.querySelector('.answer-hidden').style.display='block';this.querySelector('.answer-label').style.display='none'">
                                        <span class="answer-label">Click to show answer</span>
                                        <span class="answer-hidden" style="display:none">Answer: ${this.fmt(p.answer || '', subject)}</span>
                                    </div>`}
                                    ${p.hint ? `<div class="problem-hint">Hint: ${App.escapeHtml(p.hint)}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    },

    renderQuizPreview(container, questions, subject) {
        if (!questions.length) {
            container.innerHTML = '<div class="studio-result"><p>No questions generated. Try a different topic from the presets.</p></div>';
            return;
        }
        container.innerHTML = `
            <div class="studio-result studio-quiz">
                <div class="studio-result-header">
                    <h2>Quiz: ${questions.length} Questions</h2>
                    <span class="studio-result-badge">${subject || ''}</span>
                </div>
                <div class="quiz-questions-list">
                    ${questions.map((q, i) => `
                        <div class="quiz-question-card">
                            <div class="problem-num">${i + 1}</div>
                            <div class="problem-body">
                                <div class="problem-question">${this.fmt(q.question, subject)}</div>
                                ${q.options ? `
                                    <div class="problem-options">
                                        ${q.options.map((o, j) => `
                                            <div class="problem-option ${j === q.correct ? 'correct' : ''}">${String.fromCharCode(65 + j)}. ${this.fmt(String(o), subject)}</div>
                                        `).join('')}
                                    </div>
                                ` : `<div class="problem-answer-inline">Answer: ${this.fmt(q.answer || '', subject)}</div>`}
                                ${q.hint ? `<div class="problem-hint">Hint: ${App.escapeHtml(q.hint)}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    renderFlashcardPreview(container, cards, subject) {
        if (!cards.length) {
            container.innerHTML = '<div class="studio-result"><p>No flashcards generated. Try a different topic from the presets.</p></div>';
            return;
        }
        container.innerHTML = `
            <div class="studio-result studio-flashcards-result">
                <div class="studio-result-header">
                    <h2>Flashcards (${cards.length})</h2>
                    <span class="studio-result-badge">${subject || ''}</span>
                </div>
                <p class="studio-result-hint">Click a card to flip it!</p>
                <div class="studio-fc-grid">
                    ${cards.map((c, i) => `
                        <div class="studio-fc-card" onclick="this.classList.toggle('flipped')">
                            <div class="studio-fc-inner">
                                <div class="studio-fc-front">
                                    <div class="studio-fc-num">${i + 1}</div>
                                    <div class="studio-fc-text">${this.fmt(c.front, subject)}</div>
                                </div>
                                <div class="studio-fc-back">
                                    <div class="studio-fc-text">${this.fmt(c.back, subject)}</div>
                                    ${c.hint ? `<div class="studio-fc-hint">${App.escapeHtml(c.hint)}</div>` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div style="text-align:center;margin-top:1rem">
                    <button class="btn btn-primary" onclick="App.navigate('flashcards-home')">Study All Flashcards</button>
                </div>
            </div>
        `;
    },

    renderPracticePreview(container, problems, subject) {
        if (!problems.length) {
            container.innerHTML = '<div class="studio-result"><p>No problems generated. Try a different topic from the presets.</p></div>';
            return;
        }
        container.innerHTML = `
            <div class="studio-result studio-practice">
                <div class="studio-result-header">
                    <h2>Practice Problems (${problems.length})</h2>
                    <span class="studio-result-badge">${subject || ''}</span>
                </div>
                ${problems.map((p, i) => `
                    <div class="problem-card">
                        <div class="problem-num">${i + 1}</div>
                        <div class="problem-body">
                            <div class="problem-question">${this.fmt(p.question, subject)}</div>
                            ${p.options ? `
                                <div class="problem-options">
                                    ${p.options.map((o, j) => `
                                        <div class="problem-option ${j === p.correct ? 'correct' : ''}">${String.fromCharCode(65 + j)}. ${this.fmt(String(o), subject)}</div>
                                    `).join('')}
                                </div>
                            ` : `
                                <div class="problem-answer-reveal" onclick="this.querySelector('.answer-hidden').style.display='block';this.querySelector('.answer-label').style.display='none'">
                                    <span class="answer-label">Click to show answer</span>
                                    <span class="answer-hidden" style="display:none">Answer: ${this.fmt(p.answer || '', subject)}</span>
                                </div>
                            `}
                            ${p.hint ? `<div class="problem-hint">Hint: ${App.escapeHtml(p.hint)}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    async loadSaved() {
        try {
            const data = await App.api('/api/generate/saved');
            const el = document.getElementById('studio-saved');
            if (!el) return;
            if (!data.items || data.items.length === 0) {
                el.innerHTML = '<p class="studio-saved-empty">No saved content yet. Generate something above!</p>';
                return;
            }
            const typeIcons = { lesson: '📖', quiz: '✅', flashcards: '🃏', practice: '✏️' };
            el.innerHTML = `
                <div class="studio-saved-grid">
                    ${data.items.map(item => `
                        <div class="studio-saved-card" onclick="Generate.viewSaved(${item.id})">
                            <div class="studio-saved-icon">${typeIcons[item.content_type] || '📄'}</div>
                            <div class="studio-saved-info">
                                <div class="studio-saved-title">${App.escapeHtml(item.topic || 'Untitled')}</div>
                                <div class="studio-saved-meta">
                                    <span class="studio-saved-type">${item.content_type}</span>
                                    <span class="studio-saved-subject ${item.subject}">${item.subject}</span>
                                    <span>Grade ${item.grade}</span>
                                </div>
                            </div>
                            <button class="btn-icon btn-icon-danger" onclick="event.stopPropagation();Generate.deleteSaved(${item.id})" title="Delete">&#128465;</button>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            const el = document.getElementById('studio-saved');
            if (el) el.innerHTML = '';
        }
    },

    async viewSaved(id) {
        try {
            const data = await App.api(`/api/generate/saved/${id}`);
            const output = document.getElementById('studio-output');
            if (!output) return;
            const subject = data.subject || '';
            if (data.content_type === 'lesson') {
                this.renderLesson(output, data.content, subject);
            } else if (data.content_type === 'quiz') {
                this.renderQuizPreview(output, data.content, subject);
            } else if (data.content_type === 'flashcards') {
                this.renderFlashcardPreview(output, data.content, subject);
            } else if (data.content_type === 'practice') {
                this.renderPracticePreview(output, data.content, subject);
            }
            output.scrollIntoView({ behavior: 'smooth' });
        } catch (e) {
            App.showToast('Error loading content', 'error');
        }
    },

    async deleteSaved(id) {
        try {
            await App.api(`/api/generate/saved/${id}`, { method: 'DELETE' });
            App.showToast('Deleted', 'success');
            this.loadSaved();
        } catch (e) {
            App.showToast('Error deleting', 'error');
        }
    }
};
