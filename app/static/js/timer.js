/**
 * LearnQuest - Pomodoro Study Timer
 * A floating widget that persists across navigation.
 */

const StudyTimer = {
    studyMinutes: 25,
    breakMinutes: 5,
    secondsRemaining: 25 * 60,
    isRunning: false,
    isBreak: false,
    isPanelOpen: false,
    _interval: null,
    _widgetCreated: false,

    /** Initialize the timer widget (called once after login) */
    init() {
        if (this._widgetCreated) return;
        this._widgetCreated = true;

        const widget = document.createElement('div');
        widget.className = 'timer-widget';
        widget.id = 'timer-widget';
        widget.innerHTML = `
            <button class="timer-fab" onclick="StudyTimer.togglePanel()" title="Study Timer">&#9201;</button>
            <div class="timer-panel hidden" id="timer-panel">
                <div class="timer-label" id="timer-label">STUDY TIME</div>
                <div class="timer-display study-mode" id="timer-display">25:00</div>
                <div class="timer-controls">
                    <button class="btn btn-primary" id="timer-start-btn" onclick="StudyTimer.toggleTimer()">Start</button>
                    <button class="btn btn-secondary" onclick="StudyTimer.reset()">Reset</button>
                </div>
                <div style="margin-top:0.75rem;font-size:0.8rem;color:var(--text-light)">
                    <label>Study: <input type="number" id="timer-study-min" value="25" min="1" max="60" style="width:40px" onchange="StudyTimer.updateDuration()">m</label>
                    <label style="margin-left:0.5rem">Break: <input type="number" id="timer-break-min" value="5" min="1" max="30" style="width:40px" onchange="StudyTimer.updateDuration()">m</label>
                </div>
            </div>
        `;
        document.body.appendChild(widget);
    },

    togglePanel() {
        this.isPanelOpen = !this.isPanelOpen;
        document.getElementById('timer-panel')?.classList.toggle('hidden', !this.isPanelOpen);
    },

    toggleTimer() {
        if (this.isRunning) {
            this.pause();
        } else {
            this.start();
        }
    },

    start() {
        this.isRunning = true;
        document.getElementById('timer-start-btn').textContent = 'Pause';

        this._interval = setInterval(() => {
            this.secondsRemaining--;
            this.updateDisplay();

            if (this.secondsRemaining <= 0) {
                this.onTimerComplete();
            }
        }, 1000);
    },

    pause() {
        this.isRunning = false;
        clearInterval(this._interval);
        document.getElementById('timer-start-btn').textContent = 'Resume';
    },

    reset() {
        this.pause();
        this.isBreak = false;
        this.secondsRemaining = this.studyMinutes * 60;
        this.updateDisplay();
        document.getElementById('timer-start-btn').textContent = 'Start';
        document.getElementById('timer-label').textContent = 'STUDY TIME';
        const display = document.getElementById('timer-display');
        if (display) {
            display.classList.add('study-mode');
            display.classList.remove('break-mode');
        }
    },

    updateDuration() {
        const studyEl = document.getElementById('timer-study-min');
        const breakEl = document.getElementById('timer-break-min');
        if (studyEl) this.studyMinutes = parseInt(studyEl.value) || 25;
        if (breakEl) this.breakMinutes = parseInt(breakEl.value) || 5;
        if (!this.isRunning) {
            this.secondsRemaining = (this.isBreak ? this.breakMinutes : this.studyMinutes) * 60;
            this.updateDisplay();
        }
    },

    updateDisplay() {
        const mins = Math.floor(this.secondsRemaining / 60);
        const secs = this.secondsRemaining % 60;
        const display = document.getElementById('timer-display');
        if (display) {
            display.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
    },

    async onTimerComplete() {
        clearInterval(this._interval);
        this.isRunning = false;

        // Play a simple sound (or beep via AudioContext)
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            osc.type = 'sine';
            osc.frequency.value = this.isBreak ? 523 : 440;
            osc.connect(ctx.destination);
            osc.start();
            setTimeout(() => osc.stop(), 500);
        } catch (e) { /* no audio */ }

        if (!this.isBreak) {
            // Study session complete - award XP bonus
            try {
                await App.api('/api/lesson/pomodoro-xp/complete', {
                    method: 'POST',
                    body: { subject: 'general', grade: App.state.user?.grade || 3, score: 100 }
                });
                await App.refreshUser();
                if (typeof Gamification !== 'undefined') {
                    Gamification.showXpGain(5);
                }
            } catch (e) { /* ignore */ }

            App.showToast('Study session complete! Take a break.', 'success');
            this.isBreak = true;
            this.secondsRemaining = this.breakMinutes * 60;
            document.getElementById('timer-label').textContent = 'BREAK TIME';
            const display = document.getElementById('timer-display');
            if (display) {
                display.classList.remove('study-mode');
                display.classList.add('break-mode');
            }
        } else {
            App.showToast('Break over! Ready for another round?', 'info');
            this.isBreak = false;
            this.secondsRemaining = this.studyMinutes * 60;
            document.getElementById('timer-label').textContent = 'STUDY TIME';
            const display = document.getElementById('timer-display');
            if (display) {
                display.classList.add('study-mode');
                display.classList.remove('break-mode');
            }
        }

        this.updateDisplay();
        document.getElementById('timer-start-btn').textContent = 'Start';
    }
};

// Auto-init timer when DOM is ready and user is logged in
document.addEventListener('DOMContentLoaded', () => {
    const origLogin = App.onLoginSuccess.bind(App);
    const wrappedLogin = App.onLoginSuccess;
    App.onLoginSuccess = function() {
        wrappedLogin.call(App);
        if (App.state.user && App.state.user.role === 'student') {
            StudyTimer.init();
        }
    };
});
