/**
 * LearnQuest - AI Tutor Chat Interface
 * Supports panel mode, full-page mode, and conversation management.
 */

const Tutor = {
    sessionId: null,
    currentLessonId: null,
    currentSubject: null,
    currentGrade: null,
    isOpen: false,
    isFullPage: false,
    _tooltipTimer: null,
    conversations: [],
    activeConversationId: null,

    /** Toggle tutor panel (slide-in) */
    toggle() {
        this.isOpen = !this.isOpen;
        const panel = document.getElementById('tutor-panel');
        panel.classList.toggle('hidden', !this.isOpen);
        this._updateHeaderColor();
        if (this.isOpen) {
            document.getElementById('tutor-input').focus();
        }
    },

    /** Set context for current lesson */
    setContext(lessonId, subject, grade) {
        this.currentLessonId = lessonId;
        this.currentSubject = subject;
        this.currentGrade = grade;
        this.sessionId = `session_${Date.now()}`;
        this._updateHeaderColor();
        const msgContainer = document.getElementById('tutor-messages');
        if (msgContainer) {
            msgContainer.innerHTML = `
                <div class="tutor-msg assistant">
                    <div class="tutor-msg-content">
                        Hi there! I'm your Learning Buddy. I can help you with this lesson. What would you like to know?
                    </div>
                </div>
            `;
        }
    },

    _updateHeaderColor() {
        const header = document.querySelector('.tutor-header');
        if (!header) return;
        header.classList.remove('math-tutor', 'science-tutor', 'ela-tutor', 'social-tutor');
        const subjectMap = { math: 'math-tutor', science: 'science-tutor', ela: 'ela-tutor', social_studies: 'social-tutor' };
        if (this.currentSubject && subjectMap[this.currentSubject]) {
            header.classList.add(subjectMap[this.currentSubject]);
        }
    },

    /** Send message to tutor (works for both panel and full-page) */
    async send(inputId) {
        const id = inputId || 'tutor-input';
        const input = document.getElementById(id);
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        const msgContainerId = this.isFullPage ? 'tutor-full-messages' : 'tutor-messages';
        this.addMessage('user', message, msgContainerId);
        const typingId = this.showTyping(msgContainerId);

        try {
            const response = await fetch('/api/tutor/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    session_id: this.sessionId || `session_${Date.now()}`,
                    lesson_id: this.currentLessonId,
                    subject: this.currentSubject || document.getElementById('tutor-subject-select')?.value || 'math',
                    grade: this.currentGrade || App.state.user?.grade
                })
            });

            this.removeTyping(typingId);

            if (response.headers.get('content-type')?.includes('text/event-stream')) {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let assistantMsg = '';
                const msgEl = this.addMessage('assistant', '', msgContainerId);
                const contentEl = msgEl.querySelector('.tutor-msg-content');

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') break;
                            try {
                                const parsed = JSON.parse(data);
                                if (parsed.token) {
                                    assistantMsg += parsed.token;
                                    contentEl.textContent = assistantMsg;
                                }
                            } catch (e) {
                                assistantMsg += data;
                                contentEl.textContent = assistantMsg;
                            }
                        }
                    }
                    this.scrollToBottom(msgContainerId);
                }
            } else {
                const data = await response.json();
                this.addMessage('assistant', data.response || data.error || 'Sorry, I had trouble understanding that.', msgContainerId);
            }

            // Refresh conversation list if on full page
            if (this.isFullPage) {
                this.loadConversations();
            }
        } catch (err) {
            this.removeTyping(typingId);
            this.addMessage('assistant', 'Oops! I had a little trouble there. Try asking again!', msgContainerId);
        }
    },

    addMessage(role, content, containerId) {
        const container = document.getElementById(containerId || 'tutor-messages');
        if (!container) return null;
        const msg = document.createElement('div');
        msg.className = `tutor-msg ${role}`;
        msg.innerHTML = `<div class="tutor-msg-content">${App.escapeHtml(content)}</div>`;
        container.appendChild(msg);
        this.scrollToBottom(containerId);
        return msg;
    },

    showTyping(containerId) {
        const id = 'typing-' + Date.now();
        const container = document.getElementById(containerId || 'tutor-messages');
        if (!container) return id;
        const el = document.createElement('div');
        el.className = 'tutor-msg assistant typing';
        el.id = id;
        el.innerHTML = '<div class="tutor-msg-content"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
        container.appendChild(el);
        this.scrollToBottom(containerId);
        return id;
    },

    removeTyping(id) {
        document.getElementById(id)?.remove();
    },

    scrollToBottom(containerId) {
        const container = document.getElementById(containerId || 'tutor-messages');
        if (container) container.scrollTop = container.scrollHeight;
    },

    async getHint(problem, subject, grade) {
        try {
            const data = await App.api('/api/tutor/hint', {
                method: 'POST',
                body: { problem, subject, grade }
            });
            return data.hint;
        } catch (err) {
            return 'Try breaking the problem into smaller steps!';
        }
    },

    /** Render full-page tutor mode with conversation sidebar */
    renderFullPage(container) {
        const user = App.state.user;
        if (!user) return App.navigate('login');

        this.isFullPage = true;
        if (!this.sessionId) {
            this.sessionId = `session_${Date.now()}`;
        }

        const prompts = [
            'Explain fractions', 'Quiz me on multiplication', 'Help with reading',
            'What is photosynthesis?', 'Help me write a paragraph', 'Explain the water cycle',
            'Practice division', 'Who was George Washington?', 'What are adjectives?'
        ];

        container.innerHTML = `
            <div class="tutor-full-layout">
                <div class="tutor-sidebar">
                    <div class="tutor-sidebar-header">
                        <h3>Conversations</h3>
                        <button class="btn btn-sm btn-primary" onclick="Tutor.newConversation()">+ New</button>
                    </div>
                    <div class="tutor-conv-list" id="tutor-conv-list">
                        <div class="tutor-conv-loading">Loading...</div>
                    </div>
                </div>
                <div class="tutor-main-chat">
                    <div class="tutor-chat-header">
                        <select id="tutor-subject-select" onchange="Tutor.currentSubject=this.value">
                            <option value="math" ${this.currentSubject === 'math' ? 'selected' : ''}>Math</option>
                            <option value="science" ${this.currentSubject === 'science' ? 'selected' : ''}>Science</option>
                            <option value="ela" ${this.currentSubject === 'ela' ? 'selected' : ''}>English</option>
                            <option value="social_studies" ${this.currentSubject === 'social_studies' ? 'selected' : ''}>Social Studies</option>
                        </select>
                    </div>

                    <div class="tutor-prompt-chips">
                        ${prompts.map(p => `<button class="prompt-chip" onclick="Tutor.sendPrompt('${p}')">${p}</button>`).join('')}
                    </div>

                    <div class="tutor-full-messages" id="tutor-full-messages">
                        <div class="tutor-msg assistant">
                            <div class="tutor-msg-content">
                                Hi ${App.escapeHtml(user.name)}! I'm your Learning Buddy. Pick a topic above or ask me anything!
                            </div>
                        </div>
                    </div>

                    <div class="tutor-full-input-area">
                        <input type="text" id="tutor-full-input" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter')Tutor.send('tutor-full-input')">
                        <button class="btn btn-primary" onclick="Tutor.send('tutor-full-input')">Send</button>
                    </div>
                </div>
            </div>
        `;

        this.loadConversations();
    },

    /** Load conversation list */
    async loadConversations() {
        try {
            const data = await App.api('/api/tutor/conversations');
            this.conversations = data.conversations || [];
            this.renderConversationList();
        } catch (e) {
            const el = document.getElementById('tutor-conv-list');
            if (el) el.innerHTML = '<div class="tutor-conv-empty">No conversations yet</div>';
        }
    },

    renderConversationList() {
        const el = document.getElementById('tutor-conv-list');
        if (!el) return;

        if (!this.conversations.length) {
            el.innerHTML = '<div class="tutor-conv-empty">No conversations yet. Start chatting!</div>';
            return;
        }

        el.innerHTML = this.conversations.map(c => {
            const isActive = c.session_id === this.sessionId;
            const dateStr = c.updated_at ? new Date(c.updated_at).toLocaleDateString() : '';
            return `
                <div class="tutor-conv-item ${isActive ? 'active' : ''}" onclick="Tutor.loadConversation(${c.id}, '${c.session_id}', '${c.subject || 'math'}')">
                    <div class="tutor-conv-item-main">
                        ${c.pinned ? '<span class="tutor-conv-pin" title="Pinned">&#128204;</span>' : ''}
                        <div class="tutor-conv-title">${App.escapeHtml(c.title)}</div>
                        <div class="tutor-conv-meta">
                            <span class="tutor-conv-subject ${c.subject || ''}">${c.subject || ''}</span>
                            <span class="tutor-conv-date">${dateStr}</span>
                            <span class="tutor-conv-count">${c.message_count || 0} msgs</span>
                        </div>
                    </div>
                    <div class="tutor-conv-actions" onclick="event.stopPropagation()">
                        <button class="btn-icon-sm" onclick="Tutor.togglePin(${c.id})" title="${c.pinned ? 'Unpin' : 'Pin'}">&#128204;</button>
                        <button class="btn-icon-sm" onclick="Tutor.renameConversation(${c.id}, '${App.escapeHtml(c.title).replace(/'/g, "\\'")}')" title="Rename">&#9998;</button>
                        <button class="btn-icon-sm btn-icon-danger" onclick="Tutor.deleteConversation(${c.id})" title="Delete">&#128465;</button>
                    </div>
                </div>
            `;
        }).join('');
    },

    /** Start a new conversation */
    newConversation() {
        this.sessionId = `session_${Date.now()}`;
        this.activeConversationId = null;
        const msgs = document.getElementById('tutor-full-messages');
        if (msgs) {
            msgs.innerHTML = `
                <div class="tutor-msg assistant">
                    <div class="tutor-msg-content">
                        Hi! Ready for a new conversation. What would you like to learn about?
                    </div>
                </div>
            `;
        }
        // Deselect in sidebar
        document.querySelectorAll('.tutor-conv-item').forEach(el => el.classList.remove('active'));
    },

    /** Load an existing conversation */
    async loadConversation(convId, sessionId, subject) {
        this.sessionId = sessionId;
        this.activeConversationId = convId;
        this.currentSubject = subject;

        // Update subject selector
        const sel = document.getElementById('tutor-subject-select');
        if (sel) sel.value = subject || 'math';

        const msgs = document.getElementById('tutor-full-messages');
        if (msgs) msgs.innerHTML = '<div class="tutor-conv-loading">Loading messages...</div>';

        try {
            const data = await App.api(`/api/tutor/conversations/${convId}/messages`);
            if (msgs) {
                if (!data.messages || data.messages.length === 0) {
                    msgs.innerHTML = `
                        <div class="tutor-msg assistant">
                            <div class="tutor-msg-content">This conversation is empty. Ask me something!</div>
                        </div>
                    `;
                } else {
                    msgs.innerHTML = data.messages.map(m => `
                        <div class="tutor-msg ${m.role === 'user' ? 'user' : 'assistant'}">
                            <div class="tutor-msg-content">${App.escapeHtml(m.message)}</div>
                        </div>
                    `).join('');
                    this.scrollToBottom('tutor-full-messages');
                }
            }

            // Highlight active conversation in sidebar
            document.querySelectorAll('.tutor-conv-item').forEach(el => el.classList.remove('active'));
            const items = document.querySelectorAll('.tutor-conv-item');
            items.forEach(el => {
                if (el.onclick?.toString().includes(sessionId)) {
                    el.classList.add('active');
                }
            });
            this.renderConversationList();
        } catch (e) {
            if (msgs) msgs.innerHTML = '<p class="error-msg">Error loading messages</p>';
        }
    },

    /** Rename conversation */
    renameConversation(convId, currentTitle) {
        const newTitle = prompt('Enter new title:', currentTitle);
        if (!newTitle || newTitle.trim() === currentTitle) return;

        App.api(`/api/tutor/conversations/${convId}`, {
            method: 'PUT',
            body: { title: newTitle.trim() }
        }).then(() => {
            this.loadConversations();
        }).catch(e => App.showToast('Error renaming', 'error'));
    },

    /** Delete conversation */
    deleteConversation(convId) {
        App.showConfirm('Delete this conversation?', async () => {
            try {
                await App.api(`/api/tutor/conversations/${convId}`, { method: 'DELETE' });
                App.showToast('Conversation deleted', 'success');
                if (this.activeConversationId === convId) {
                    this.newConversation();
                }
                this.loadConversations();
            } catch (e) {
                App.showToast('Error deleting', 'error');
            }
        });
    },

    /** Toggle pin */
    async togglePin(convId) {
        try {
            await App.api(`/api/tutor/conversations/${convId}/pin`, { method: 'POST' });
            this.loadConversations();
        } catch (e) {
            App.showToast('Error', 'error');
        }
    },

    sendPrompt(text) {
        const input = document.getElementById(this.isFullPage ? 'tutor-full-input' : 'tutor-input');
        if (input) {
            input.value = text;
            this.send(input.id);
        }
    },

    updateForPage(page, params) {
        this.isFullPage = (page === 'tutor');
        this._dismissTooltip();
        if (page === 'lesson' && params) {
            this._tooltipTimer = setTimeout(() => {
                if (localStorage.getItem('tutorTipsDismissed') !== 'true') {
                    this._showTooltip('Need help understanding this lesson? Click here to ask!');
                }
            }, 3000);
        }
    },

    _showTooltip(message) {
        this._dismissTooltip();
        const tooltip = document.createElement('div');
        tooltip.className = 'tutor-tooltip';
        tooltip.id = 'tutor-tooltip';
        tooltip.innerHTML = `
            <button class="tutor-tooltip-close" onclick="Tutor._dismissTooltip();localStorage.setItem('tutorTipsDismissed','true')">x</button>
            <span onclick="Tutor.toggle();Tutor._dismissTooltip()" style="cursor:pointer">${message}</span>
        `;
        document.body.appendChild(tooltip);
        setTimeout(() => this._dismissTooltip(), 8000);
    },

    _dismissTooltip() {
        clearTimeout(this._tooltipTimer);
        document.getElementById('tutor-tooltip')?.remove();
    },

    showWrongAnswerTip() {
        if (localStorage.getItem('tutorTipsDismissed') !== 'true') {
            this._showTooltip('Want me to explain this? Click here!');
        }
    }
};
