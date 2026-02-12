/**
 * LearnQuest - Flashcard System
 * Supports manual cards, AI-generated cards, and Leitner spaced repetition.
 */

const Flashcards = {
    currentCards: [],
    currentIndex: 0,
    isFlipped: false,

    /** Render flashcard home page */
    async renderHome(container) {
        const user = App.state.user;
        if (!user) return App.navigate('login');

        container.innerHTML = `
            <div class="page-container">
                <h1>Flashcards</h1>
                <p>Study with flip cards! Click a card to reveal the answer.</p>

                <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1.5rem">
                    <button class="btn btn-primary" onclick="Flashcards.startStudy()">Study Due Cards</button>
                    <button class="btn btn-secondary" onclick="Flashcards.showCreateForm()">Create New Card</button>
                    <button class="btn btn-accent" onclick="App.navigate('ai-studio')">Generate with AI</button>
                </div>

                <div id="flashcard-create-area"></div>

                <h2>My Cards</h2>
                <div class="flashcard-filter">
                    <select id="fc-filter-subject" onchange="Flashcards.loadCards()">
                        <option value="">All Subjects</option>
                        <option value="math">Math</option>
                        <option value="science">Science</option>
                        <option value="ela">ELA</option>
                        <option value="social_studies">Social Studies</option>
                    </select>
                </div>
                <div id="flashcard-list">Loading...</div>
            </div>
        `;

        this.loadCards();
    },

    showCreateForm() {
        const area = document.getElementById('flashcard-create-area');
        area.innerHTML = `
            <div class="studio-result" style="margin-bottom:1rem">
                <h3>New Flashcard</h3>
                <div class="form-group">
                    <label>Front (Question/Term)</label>
                    <input type="text" id="fc-new-front" placeholder="e.g., What is the capital of France?">
                </div>
                <div class="form-group">
                    <label>Back (Answer/Definition)</label>
                    <input type="text" id="fc-new-back" placeholder="e.g., Paris">
                </div>
                <div class="form-group">
                    <label>Hint (optional)</label>
                    <input type="text" id="fc-new-hint" placeholder="e.g., Starts with P">
                </div>
                <div class="form-group">
                    <label>Subject</label>
                    <select id="fc-new-subject">
                        <option value="math">Math</option>
                        <option value="science">Science</option>
                        <option value="ela">ELA</option>
                        <option value="social_studies">Social Studies</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="Flashcards.createCard()">Add Card</button>
                <button class="btn btn-secondary" onclick="document.getElementById('flashcard-create-area').innerHTML=''">Cancel</button>
            </div>
        `;
    },

    async createCard() {
        const front = document.getElementById('fc-new-front').value.trim();
        const back = document.getElementById('fc-new-back').value.trim();
        const hint = document.getElementById('fc-new-hint').value.trim();
        const subject = document.getElementById('fc-new-subject').value;

        if (!front || !back) {
            App.showToast('Front and back are required', 'error');
            return;
        }

        try {
            await App.api('/api/flashcards', {
                method: 'POST',
                body: { front, back, hint, subject, grade: App.state.user.grade }
            });
            App.showToast('Flashcard created!', 'success');
            document.getElementById('flashcard-create-area').innerHTML = '';
            this.loadCards();
        } catch (e) {
            App.showToast('Error: ' + e.message, 'error');
        }
    },

    async loadCards() {
        const subject = document.getElementById('fc-filter-subject')?.value || '';
        try {
            const params = subject ? `?subject=${subject}` : '';
            const data = await App.api(`/api/flashcards${params}`);
            const el = document.getElementById('flashcard-list');
            if (!el) return;

            const cards = data.flashcards || [];
            if (cards.length === 0) {
                el.innerHTML = '<p style="color:var(--text-light)">No flashcards yet. Create some or generate with AI!</p>';
                return;
            }

            el.innerHTML = `
                <div class="flashcard-grid">
                    ${cards.map(c => `
                        <div class="flashcard-deck" onclick="this.querySelector('.fc-back').classList.toggle('hidden')">
                            <div class="fc-front"><strong>${App.escapeHtml(c.front)}</strong></div>
                            <div class="fc-back hidden" style="margin-top:0.5rem;color:var(--secondary)">${App.escapeHtml(c.back)}</div>
                            <div style="margin-top:0.5rem;font-size:0.75rem;color:var(--text-light)">
                                ${c.subject || ''} ${c.box ? '| Box ' + c.box : ''}
                                <button class="btn-icon btn-icon-danger" style="font-size:0.7rem" onclick="event.stopPropagation();Flashcards.deleteCard(${c.id})">x</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            const el = document.getElementById('flashcard-list');
            if (el) el.innerHTML = '<p class="error-msg">Error loading flashcards</p>';
        }
    },

    async deleteCard(id) {
        try {
            await App.api(`/api/flashcards/${id}`, { method: 'DELETE' });
            this.loadCards();
        } catch (e) {
            App.showToast('Error deleting card', 'error');
        }
    },

    /** Start a study session with due cards */
    async startStudy(subject) {
        try {
            const params = subject ? `?subject=${subject}` : '';
            const data = await App.api(`/api/flashcards/study${params}`);
            this.currentCards = data.cards || [];
            this.currentIndex = 0;
            this.isFlipped = false;

            if (this.currentCards.length === 0) {
                App.showToast('No cards due for review! Create some first.', 'info');
                return;
            }

            App.navigate('flashcards-study', { subject });
        } catch (e) {
            App.showToast('Error: ' + e.message, 'error');
        }
    },

    /** Render the study view */
    renderStudy(container, subject, grade) {
        const user = App.state.user;
        if (!user || this.currentCards.length === 0) {
            return App.navigate('flashcards-home');
        }

        this.renderCurrentCard(container);
    },

    renderCurrentCard(container) {
        const card = this.currentCards[this.currentIndex];
        if (!card) {
            container.innerHTML = `
                <div class="page-container" style="text-align:center">
                    <h1>Study Session Complete!</h1>
                    <p>You reviewed ${this.currentCards.length} cards.</p>
                    <button class="btn btn-primary" onclick="App.navigate('flashcards-home')">Back to Flashcards</button>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="page-container" style="text-align:center">
                <button class="btn btn-secondary" onclick="App.navigate('flashcards-home')" style="float:left">Back</button>
                <div class="flashcard-counter">Card ${this.currentIndex + 1} of ${this.currentCards.length}</div>

                <div class="flashcard-container">
                    <div class="flashcard ${this.isFlipped ? 'flipped' : ''}" onclick="Flashcards.flip()">
                        <div class="flashcard-face flashcard-front">
                            <div>
                                <div style="font-size:1.3rem;font-weight:600">${App.escapeHtml(card.front)}</div>
                                ${card.hint ? `<div style="font-size:0.85rem;color:var(--text-light);margin-top:0.5rem">Hint: ${App.escapeHtml(card.hint)}</div>` : ''}
                                <div style="font-size:0.8rem;color:var(--text-light);margin-top:1rem">Click to flip</div>
                            </div>
                        </div>
                        <div class="flashcard-face flashcard-back">
                            <div>${App.escapeHtml(card.back)}</div>
                        </div>
                    </div>
                </div>

                <div class="flashcard-controls" id="fc-study-controls" style="display:${this.isFlipped ? 'flex' : 'none'}">
                    <button class="btn fc-btn-got-it" onclick="Flashcards.reviewCard(true)">Got it!</button>
                    <button class="btn fc-btn-learning" onclick="Flashcards.reviewCard(false)">Still learning</button>
                </div>
            </div>
        `;
    },

    flip() {
        this.isFlipped = !this.isFlipped;
        const card = document.querySelector('.flashcard');
        if (card) card.classList.toggle('flipped', this.isFlipped);
        const controls = document.getElementById('fc-study-controls');
        if (controls) controls.style.display = this.isFlipped ? 'flex' : 'none';
    },

    async reviewCard(correct) {
        const card = this.currentCards[this.currentIndex];
        if (!card) return;

        try {
            await App.api('/api/flashcards/review', {
                method: 'POST',
                body: { flashcard_id: card.id, correct }
            });
        } catch (e) { /* ignore */ }

        this.currentIndex++;
        this.isFlipped = false;
        this.renderCurrentCard(document.getElementById('main-content'));
    }
};
