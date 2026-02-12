/**
 * LearnQuest - Vocabulary Builder
 * Collects key_vocabulary from completed lessons and provides study tools.
 */

const Vocabulary = {
    async renderPage(container) {
        const user = App.state.user;
        if (!user) return App.navigate('login');

        container.innerHTML = `
            <div class="page-container">
                <h1>Vocabulary Builder</h1>
                <p>All the key words from your completed lessons.</p>

                <div class="vocab-filter">
                    <select id="vocab-subject-filter" onchange="Vocabulary.loadWords()">
                        <option value="">All Subjects</option>
                        <option value="math">Math</option>
                        <option value="science">Science</option>
                        <option value="ela">ELA</option>
                        <option value="social_studies">Social Studies</option>
                    </select>
                    <input type="text" id="vocab-search" placeholder="Filter words..." oninput="Vocabulary.filterWords()" style="padding:0.4rem 0.8rem;border:2px solid var(--border);border-radius:var(--radius-sm)">
                </div>

                <div id="vocab-word-list">Loading...</div>
            </div>
        `;

        this.loadWords();
    },

    async loadWords() {
        const subject = document.getElementById('vocab-subject-filter')?.value || '';
        try {
            const params = subject ? `?subject=${subject}` : '';
            const data = await App.api(`/api/vocabulary${params}`);
            this._words = data.words || [];
            this.renderWords(this._words);
        } catch (e) {
            document.getElementById('vocab-word-list').innerHTML = '<p class="error-msg">Error loading vocabulary</p>';
        }
    },

    renderWords(words) {
        const el = document.getElementById('vocab-word-list');
        if (!el) return;

        if (words.length === 0) {
            el.innerHTML = '<p style="color:var(--text-light)">No vocabulary words yet. Complete some lessons to build your word bank!</p>';
            return;
        }

        el.innerHTML = `
            <p style="color:var(--text-light);margin-bottom:0.5rem">${words.length} words</p>
            <div class="vocab-page-grid">
                ${words.map(w => `
                    <div class="vocab-word-card">
                        <div class="word">${App.escapeHtml(w.word)}</div>
                        <div class="source">${App.escapeHtml(w.subject)} - ${App.escapeHtml(w.lesson_title || '')}</div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    filterWords() {
        const query = (document.getElementById('vocab-search')?.value || '').toLowerCase();
        if (!this._words) return;
        const filtered = this._words.filter(w => w.word.toLowerCase().includes(query));
        this.renderWords(filtered);
    }
};
