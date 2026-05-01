

const SETTINGS_KEY = 'rsvp_settings_v2';
const DEFAULT_SETTINGS = {
    orpEnabled: true,
    punctuationPause: true,
    adaptiveSpeed: false,
    longWordPause: true,
    punctuationFactor: 1.8
};

const SPEED_MIN = 100;
const SPEED_MAX = 600;
const ADAPTIVE_STEP = 20;
const ADAPTIVE_EVERY_WORDS = 40;
const ADAPTIVE_MAX_EXTRA = 180;

let words = JSON.parse(localStorage.getItem('words')) || [];
let baseSpeed = clamp(parseInt(localStorage.getItem('speed'), 10) || 200, SPEED_MIN, SPEED_MAX);
let currentSpeed = baseSpeed;
let filename = localStorage.getItem('filename') || 'Tai lieu';
let docId = localStorage.getItem('doc_id');
let totalWords = parseInt(localStorage.getItem('total_words'), 10) || words.length;

let settings = loadSettings();

let currentIndex = 0;
let timeoutId = null;
let timerInterval = null;
let startTime = null;
let pausedTime = 0;
let isPaused = false;
let isRunning = false;
let hasCompleted = false;

const dom = {};

document.addEventListener('DOMContentLoaded', () => {
    cacheDom();
    bindEvents();
    initializeReader();
});

// If navigating from Documents with intent to choose speed, show completion overlay chooser
function checkPendingShowChooser() {
    try {
        const pending = localStorage.getItem('pendingShowCompletionSpeedChooser');
        if (pending === '1') {
            localStorage.removeItem('pendingShowCompletionSpeedChooser');
            // show completion overlay and the internal speed selection UI
            if (dom.completionOverlay) dom.completionOverlay.classList.add('show');
            if (dom.completionSpeedSelection) dom.completionSpeedSelection.style.display = 'block';
            dom.chooserSource = 'documents';
            const cur = Math.round(baseSpeed || 200);
            if (dom.completionSpeedSlider) dom.completionSpeedSlider.value = cur;
            if (dom.completionSpeedValue) dom.completionSpeedValue.textContent = cur;
            // update presets visual state
            activateClosestCompletionPreset(cur);
        }
    } catch (e) {
        console.warn('checkPendingShowChooser error', e);
    }
}

function cacheDom() {
    dom.wordDisplay = document.getElementById('wordDisplay');
    dom.total = document.getElementById('total');
    dom.currentSpeed = document.getElementById('currentSpeed');
    dom.speedMeta = document.getElementById('speedMeta');
    dom.progress = document.getElementById('progress');
    dom.percentage = document.getElementById('percentage');
    dom.timer = document.getElementById('timer');
    dom.playPauseBtn = document.getElementById('playPauseBtn');
    dom.readAgainBtn = document.getElementById('readAgainBtn');
    dom.backToDashboardBtn = document.getElementById('backToDashboardBtn');
    dom.completionOverlay = document.getElementById('completionOverlay');
    dom.confettiLayer = document.getElementById('confettiLayer');
    dom.documentContentPanel = document.getElementById('documentContentPanel');
    dom.documentContent = document.getElementById('documentContent');
    dom.completionSpeedSelection = document.getElementById('completionSpeedSelection');
    dom.completionSpeedSlider = document.getElementById('completionSpeedSlider');
    dom.completionSpeedValue = document.getElementById('completionSpeedValue');
    dom.completionSpeedPresets = document.getElementById('completionSpeedPresets');
    dom.completionStartBtn = document.getElementById('completionStartBtn');
    dom.completionCancelBtn = document.getElementById('completionCancelBtn');
    dom.completionHeader = document.querySelector('.completion-header');
    dom.completionActions = document.querySelector('.completion-actions');
    // track where the chooser was opened from: 'documents' | 'completion' | null
    dom.chooserSource = null;
    dom.orpToggle = document.getElementById('orpToggle');
    dom.punctuationPauseToggle = document.getElementById('punctuationPauseToggle');
    dom.adaptiveSpeedToggle = document.getElementById('adaptiveSpeedToggle');
    dom.longWordPauseToggle = document.getElementById('longWordPauseToggle');
    dom.punctuationFactor = document.getElementById('punctuationFactor');
    dom.punctuationFactorValue = document.getElementById('punctuationFactorValue');
}

function bindEvents() {
    if (dom.readAgainBtn) {
        dom.readAgainBtn.addEventListener('click', () => {
            // show speed selector inside the completion overlay
            if (dom.completionSpeedSelection) {
                // hide the header and actions so only the chooser is visible
                if (dom.completionHeader) dom.completionHeader.style.display = 'none';
                if (dom.completionActions) dom.completionActions.style.display = 'none';
                dom.completionSpeedSelection.style.display = 'block';
                dom.chooserSource = 'completion';
                // sync slider to current baseSpeed
                const cur = Math.round(baseSpeed || 200);
                if (dom.completionSpeedSlider) dom.completionSpeedSlider.value = cur;
                if (dom.completionSpeedValue) dom.completionSpeedValue.textContent = cur;
                // update presets visual state
                activateClosestCompletionPreset(cur);
            } else {
                hideCompletionOverlay();
                resetReading();
            }
        });
    }

    if (dom.backToDashboardBtn) {
        dom.backToDashboardBtn.addEventListener('click', () => {
            hideCompletionOverlay();
            goBack(true, true);
        });
    }

    if (dom.orpToggle) {
        dom.orpToggle.addEventListener('change', () => {
            settings.orpEnabled = dom.orpToggle.checked;
            saveSettings();
            if (currentIndex > 0 && currentIndex <= words.length) {
                displayWord(words[currentIndex - 1]);
            }
        });
    }

    if (dom.punctuationPauseToggle) {
        dom.punctuationPauseToggle.addEventListener('change', () => {
            settings.punctuationPause = dom.punctuationPauseToggle.checked;
            saveSettings();
        });
    }

    if (dom.adaptiveSpeedToggle) {
        dom.adaptiveSpeedToggle.addEventListener('change', () => {
            settings.adaptiveSpeed = dom.adaptiveSpeedToggle.checked;
            if (!settings.adaptiveSpeed) {
                currentSpeed = baseSpeed;
                updateSpeedDisplay();
            }
            saveSettings();
        });
    }

    if (dom.longWordPauseToggle) {
        dom.longWordPauseToggle.addEventListener('change', () => {
            settings.longWordPause = dom.longWordPauseToggle.checked;
            saveSettings();
        });
    }

    if (dom.punctuationFactor) {
        dom.punctuationFactor.addEventListener('input', () => {
            settings.punctuationFactor = clampNumber(parseFloat(dom.punctuationFactor.value), 1, 3);
            updatePunctuationFactorLabel();
            saveSettings();
        });
    }

    // completion overlay speed selector events
    if (dom.completionSpeedSlider) {
        dom.completionSpeedSlider.addEventListener('input', (e) => {
            const v = parseInt(e.target.value, 10) || 200;
            if (dom.completionSpeedValue) dom.completionSpeedValue.textContent = v;
            activateClosestCompletionPreset(v);
        });
    }
    if (dom.completionSpeedPresets) {
        const presets = dom.completionSpeedPresets.querySelectorAll('.preset');
        presets.forEach(p => {
            p.addEventListener('click', () => {
                const val = parseInt(p.getAttribute('data-value'), 10) || 200;
                if (dom.completionSpeedSlider) dom.completionSpeedSlider.value = val;
                if (dom.completionSpeedValue) dom.completionSpeedValue.textContent = val;
                activateClosestCompletionPreset(val);
            });
        });
    }
    if (dom.completionStartBtn) {
        dom.completionStartBtn.addEventListener('click', () => {
            const chosen = dom.completionSpeedSlider ? parseInt(dom.completionSpeedSlider.value, 10) : baseSpeed;
            // apply speed, persist and restart reading
            baseSpeed = clamp(chosen, SPEED_MIN, SPEED_MAX);
            currentSpeed = baseSpeed;
            localStorage.setItem('speed', String(baseSpeed));
            // hide speed selector and overlay, reset and start
            if (dom.completionSpeedSelection) dom.completionSpeedSelection.style.display = 'none';
            dom.chooserSource = null;
            hideCompletionOverlay();
            resetReading();
            startReading();
        });
    }
    if (dom.completionCancelBtn) {
        dom.completionCancelBtn.addEventListener('click', () => {
            // If chooser was opened from Documents, navigate back to documents list
            if (dom.chooserSource === 'documents') {
                localStorage.removeItem('pendingShowCompletionSpeedChooser');
                dom.chooserSource = null;
                window.location.href = '/user/documents';
                return;
            }
            // otherwise hide the entire overlay and restore UI
            dom.chooserSource = null;
            hideCompletionOverlay();
        });
    }

    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// helpers for completion overlay speed UI
function activateClosestCompletionPreset(currentValue) {
    if (!dom.completionSpeedPresets) return;
    const presets = dom.completionSpeedPresets.querySelectorAll('.preset');
    if (!presets || presets.length === 0) return;
    let closest = null; let bestDiff = Infinity;
    presets.forEach(p => {
        const val = parseInt(p.getAttribute('data-value'), 10) || 0;
        const diff = Math.abs(val - currentValue);
        if (diff < bestDiff) { bestDiff = diff; closest = p; }
    });
    presets.forEach(p => {
        const dot = p.querySelector('.dot');
        if (p === closest) {
            p.classList.add('active'); p.setAttribute('aria-pressed','true'); if (dot) dot.style.background = 'linear-gradient(135deg,#667eea,#764ba2)';
        } else { p.classList.remove('active'); p.setAttribute('aria-pressed','false'); if (dot) dot.style.background = '#cbd5e1'; }
    });
    // (no textual range label in completion overlay anymore)
}


function initializeReader() {
    syncSettingsToUI();
    updatePunctuationFactorLabel();
    updateSpeedDisplay();

    if (dom.total) {
        dom.total.textContent = totalWords;
    }

    updateButton('play');

    if (words.length === 0) {
        if (dom.wordDisplay) {
            dom.wordDisplay.textContent = 'Không có dữ liệu đọc. Vui lòng quay lại và tải tài liệu.';
        }
        return;
    }

    setIdleDisplay();
    // check if we need to show chooser immediately (navigated from Documents)
    checkPendingShowChooser();
}

function setIdleDisplay() {
    if (dom.wordDisplay) {
        dom.wordDisplay.textContent = 'Nhấn Play để bắt đầu';
    }
    if (dom.timer) dom.timer.textContent = '00:00';
    if (dom.progress) dom.progress.textContent = '0';
    if (dom.percentage) dom.percentage.textContent = '0';
}
function togglePlayPause() {
    if (words.length === 0) {
        alert('Không có dữ liệu đọc.');
        return;
    }

    if (isRunning) {
        pauseReading();
    } else {
        startReading();
    }
}

function startReading() {
    if (!startTime) {
        startTime = Date.now();
        startTimer();
    }

    if (isPaused) {
        isPaused = false;
        startTime = Date.now() - pausedTime;
    }

    isRunning = true;
    clearTimeout(timeoutId);

    runNextWord();
    updateButton('pause');
}

function runNextWord() {
    if (!isRunning) {
        return;
    }

    if (currentIndex >= words.length) {
        finishReading();
        return;
    }

    const word = words[currentIndex];
    displayWord(word);
    currentIndex += 1;
    updateProgress();
    updatePercentage();
    applyAdaptiveSpeedIfNeeded();

    const delay = computeDelay(word);
    timeoutId = setTimeout(runNextWord, delay);
}

function displayWord(word) {
    if (!dom.wordDisplay) {
        return;
    }

    if (settings.orpEnabled) {
        dom.wordDisplay.innerHTML = buildOrpWordMarkup(word);
    } else {
        dom.wordDisplay.textContent = word;
    }
}

function buildOrpWordMarkup(word) {
    const pivotIndex = getPivotIndex(word);

    if (pivotIndex < 0 || pivotIndex >= word.length) {
        return escapeHtml(word);
    }

    const left = escapeHtml(word.slice(0, pivotIndex));
    const pivot = escapeHtml(word.charAt(pivotIndex));
    const right = escapeHtml(word.slice(pivotIndex + 1));

    return `<span class="rsvp-word">${left}<span class="orp-char">${pivot}</span>${right}</span>`;
}

function getPivotIndex(word) {
    if (!word || word.length === 0) {
        return 0;
    }

    const core = getCoreWordBounds(word);
    const coreLength = core.end - core.start;

    if (coreLength <= 0) {
        return Math.floor((word.length - 1) / 2);
    }

    const corePivot = pivotByLength(coreLength);
    return Math.min(core.start + corePivot, core.end - 1);
}

function getCoreWordBounds(word) {
    let start = 0;
    let end = word.length;

    while (start < end && isSkippableEdgeChar(word.charAt(start))) {
        start += 1;
    }
    while (end > start && isSkippableEdgeChar(word.charAt(end - 1))) {
        end -= 1;
    }

    return { start, end };
}

function isSkippableEdgeChar(char) {
    return /[\s"'()[\]{}.,!?;:-]/.test(char);
}

function pivotByLength(length) {
    if (length <= 2) return 0;
    if (length <= 5) return 1;
    if (length <= 9) return 2;
    if (length <= 13) return 3;
    return 4;
}

function computeDelay(word) {
    let delay = 60000 / Math.max(currentSpeed, 60);

    if (settings.longWordPause) {
        const cleanedLength = getTimingLength(word);
        if (cleanedLength >= 10) {
            delay *= 1.2;
        }
        if (cleanedLength >= 14) {
            delay *= 1.35;
        }
    }

    if (settings.punctuationPause) {
        if (/[.!?]["')\]]*$/.test(word)) {
            delay *= settings.punctuationFactor;
        } else if (/[,;:]["')\]]*$/.test(word)) {
            delay *= Math.max(1.15, settings.punctuationFactor - 0.45);
        }
    }

    return Math.max(30, Math.round(delay));
}

function getTimingLength(word) {
    return word
        .replace(/^[\s"'([{-]+/, '')
        .replace(/[\s"')\]}.,!?;:-]+$/, '')
        .length;
}

function applyAdaptiveSpeedIfNeeded() {
    if (!settings.adaptiveSpeed || currentIndex === 0) {
        return;
    }

    const adaptiveMax = Math.min(SPEED_MAX, baseSpeed + ADAPTIVE_MAX_EXTRA);
    if (currentIndex % ADAPTIVE_EVERY_WORDS === 0 && currentSpeed < adaptiveMax) {
        currentSpeed = Math.min(currentSpeed + ADAPTIVE_STEP, adaptiveMax);
        updateSpeedDisplay();
    }
}

function pauseReading() {
    clearTimeout(timeoutId);
    timeoutId = null;
    isRunning = false;
    isPaused = true;

    if (startTime) {
        pausedTime = Date.now() - startTime;
    }

    updateButton('resume');
}

function resetReading() {
    clearTimeout(timeoutId);
    clearInterval(timerInterval);

    timeoutId = null;
    timerInterval = null;
    currentIndex = 0;
    startTime = null;
    pausedTime = 0;
    isPaused = false;
    isRunning = false;
    hasCompleted = false;
    currentSpeed = baseSpeed;

    setIdleDisplay();
    updateSpeedDisplay();
    updateButton('play');
    hideCompletionOverlay();
}

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if (isRunning && startTime && dom.timer) {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            dom.timer.textContent = `${pad2(minutes)}:${pad2(seconds)}`;
        }
    }, 1000);
}

function updateProgress() {
    if (dom.progress) {
        dom.progress.textContent = currentIndex;
    }
}

function updatePercentage() {
    if (dom.percentage) {
        const percent = totalWords > 0 ? Math.round((currentIndex / totalWords) * 100) : 0;
        dom.percentage.textContent = percent;
    }
}

function updateSpeedDisplay() {
    if (dom.currentSpeed) {
        dom.currentSpeed.textContent = Math.round(currentSpeed);
    }

    if (dom.speedMeta) {
        if (settings.adaptiveSpeed) {
            dom.speedMeta.textContent = `Cơ bản ${Math.round(baseSpeed)} | Hiện ${Math.round(currentSpeed)}`;
        } else {
            dom.speedMeta.textContent = `Cơ bản ${Math.round(baseSpeed)}`;
        }
    }
}

function updatePunctuationFactorLabel() {
    if (dom.punctuationFactorValue) {
        dom.punctuationFactorValue.textContent = `${settings.punctuationFactor.toFixed(1)}x`;
    }
}

function updateButton(state) {
    const btn = dom.playPauseBtn;
    if (!btn) return;

    if (state === 'play') {
        btn.innerHTML = '<i class="fas fa-play"></i><span>Play</span>';
        btn.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
        return;
    }

    if (state === 'pause') {
        btn.innerHTML = '<i class="fas fa-pause"></i><span>Tạm dừng</span>';
        btn.style.background = 'linear-gradient(135deg, #f59e0b, #d97706)';
        return;
    }

    btn.innerHTML = '<i class="fas fa-play"></i><span>Tiếp tục</span>';
    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
}

async function finishReading() {
    clearTimeout(timeoutId);
    clearInterval(timerInterval);
    timeoutId = null;
    timerInterval = null;
    isRunning = false;
    isPaused = false;
    hasCompleted = true;

    const totalTime = Math.max(1, Math.floor((Date.now() - startTime) / 1000));
    const effectiveSpeed = calculateEffectiveSpeed(totalTime, currentIndex);

    try {
        await API.saveSession({
            doc_id: docId,
            filename,
            total_words: totalWords,
            words_read: currentIndex,
            speed: effectiveSpeed,
            duration: totalTime,
            completed: currentIndex === totalWords
        });
    } catch (error) {
        console.error('Error saving session:', error);
    }

    showCompletionOverlay({
        totalWords,
        wordsRead: currentIndex,
        durationSeconds: totalTime,
        speed: effectiveSpeed
    });
}

function goBack(skipConfirm = false, skipSave = false) {
    if (!skipConfirm) {
        const shouldLeave = confirm('Bạn có chắc muốn thoát? Tiến độ hiện tại sẽ được lưu.');
        if (!shouldLeave) {
            return;
        }
    }

    if (!skipSave && startTime && currentIndex > 0 && !hasCompleted) {
        const totalTime = Math.max(1, Math.floor((Date.now() - startTime) / 1000));

        API.saveSession({
            doc_id: docId,
            filename,
            total_words: totalWords,
            words_read: currentIndex,
            speed: calculateEffectiveSpeed(totalTime, currentIndex),
            duration: totalTime,
            completed: false
        }).catch((error) => {
            console.error('Error saving session:', error);
        });
    }

    window.location.href = '/user/dashboard';
}

function changeSpeed(delta) {
    baseSpeed = clamp(Math.round(baseSpeed + delta), SPEED_MIN, SPEED_MAX);
    currentSpeed = baseSpeed;
    localStorage.setItem('speed', String(baseSpeed));
    updateSpeedDisplay();

    if (isRunning) {
        clearTimeout(timeoutId);
        runNextWord();
    }
}

function handleKeyboardShortcuts(event) {
    const activeTag = document.activeElement?.tagName;
    if (activeTag === 'INPUT' || activeTag === 'TEXTAREA') {
        return;
    }

    if (event.code === 'Space') {
        event.preventDefault();
        togglePlayPause();
        return;
    }

    if (event.code === 'ArrowLeft') {
        event.preventDefault();
        changeSpeed(-25);
        return;
    }

    if (event.code === 'ArrowRight') {
        event.preventDefault();
        changeSpeed(25);
        return;
    }

    if (event.code === 'KeyR') {
        event.preventDefault();
        resetReading();
    }
}

function syncSettingsToUI() {
    if (dom.orpToggle) dom.orpToggle.checked = settings.orpEnabled;
    if (dom.punctuationPauseToggle) dom.punctuationPauseToggle.checked = settings.punctuationPause;
    if (dom.adaptiveSpeedToggle) dom.adaptiveSpeedToggle.checked = settings.adaptiveSpeed;
    if (dom.longWordPauseToggle) dom.longWordPauseToggle.checked = settings.longWordPause;
    if (dom.punctuationFactor) dom.punctuationFactor.value = String(settings.punctuationFactor);
}

function loadSettings() {
    try {
        const raw = localStorage.getItem(SETTINGS_KEY);
        if (!raw) {
            return { ...DEFAULT_SETTINGS };
        }

        const parsed = JSON.parse(raw);
        return {
            ...DEFAULT_SETTINGS,
            ...parsed,
            punctuationFactor: clampNumber(
                typeof parsed.punctuationFactor === 'number' ? parsed.punctuationFactor : DEFAULT_SETTINGS.punctuationFactor,
                1,
                3
            )
        };
    } catch (error) {
        console.warn('Cannot parse RSVP settings:', error);
        return { ...DEFAULT_SETTINGS };
    }
}

function saveSettings() {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

function showCompletionOverlay({ totalWords: total, wordsRead, durationSeconds, speed }) {
    if (!dom.completionOverlay || !dom.confettiLayer) {
        return;
    }

    const completeTotal = document.getElementById('completeTotal');
    const completeRead = document.getElementById('completeRead');
    const completeTime = document.getElementById('completeTime');
    const completeSpeed = document.getElementById('completeSpeed');

    if (completeTotal) completeTotal.textContent = total;
    if (completeRead) completeRead.textContent = wordsRead;
    if (completeTime) completeTime.textContent = formatDuration(durationSeconds);
    if (completeSpeed) completeSpeed.textContent = `${speed} tu/phut`;

    dom.completionOverlay.classList.add('show');
    launchConfetti(dom.confettiLayer);

    // fetch and display document content if available
    try {
        if (docId) {
            API.getDocumentContent(docId).then((resp) => {
                if (resp && resp.success && dom.documentContentPanel && dom.documentContent) {
                    dom.documentContent.textContent = resp.text || '';
                    dom.documentContentPanel.style.display = 'block';
                }
            }).catch((err) => {
                console.warn('Không lấy được nội dung tài liệu:', err);
            });
        }
    } catch (e) {
        console.warn('Lỗi khi lấy nội dung tài liệu:', e);
    }
    // If API didn't populate content (no docId or API failed), fall back to local `words`
    try {
        if (dom.documentContentPanel && dom.documentContent && dom.documentContentPanel.style.display === 'none') {
            if (words && words.length > 0) {
                dom.documentContent.textContent = words.join(' ');
                dom.documentContentPanel.style.display = 'block';
            }
        }
    } catch (e) {
        /* ignore */
    }
}

function hideCompletionOverlay() {
    if (dom.completionOverlay) {
        dom.completionOverlay.classList.remove('show');
    }
    if (dom.confettiLayer) {
        dom.confettiLayer.innerHTML = '';
    }
    if (dom.documentContentPanel) {
        dom.documentContentPanel.style.display = 'none';
    }
    if (dom.documentContent) {
        dom.documentContent.textContent = '';
    }
    // clear any displayed content
    // restore header and actions visibility (in case they were hidden by 'Đọc lại')
    try {
        if (dom.completionHeader) dom.completionHeader.style.display = '';
        if (dom.completionActions) dom.completionActions.style.display = '';
        if (dom.completionSpeedSelection) dom.completionSpeedSelection.style.display = 'none';
    } catch (e) {
        // ignore
    }
}

/* horizontal scroller removed - using native scrollbars and simple content rendering */

function launchConfetti(confettiLayer) {
    confettiLayer.innerHTML = '';

    const canvas = document.createElement('canvas');
    canvas.id = 'fireworksCanvas';
    confettiLayer.appendChild(canvas);

    const rect = confettiLayer.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
        return;
    }

    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.globalCompositeOperation = 'lighter';

    const palette = [
        [255, 99, 71],
        [255, 195, 0],
        [64, 224, 208],
        [0, 153, 255],
        [255, 105, 180],
        [124, 77, 255]
    ];

    const bursts = [];
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const burstCount = 3;
    const burstDelay = 220;
    const gravity = 0.035;
    const friction = 0.988;

    function createBurst() {
        const color = palette[Math.floor(Math.random() * palette.length)];
        const count = 140 + Math.floor(Math.random() * 40);
        const particles = [];
        const offsetX = (Math.random() - 0.5) * 40;
        const offsetY = (Math.random() - 0.5) * 40;
        const originX = centerX + offsetX;
        const originY = centerY + offsetY;

        for (let i = 0; i < count; i += 1) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 2.2 + Math.random() * 3.6;
            particles.push({
                x: originX,
                y: originY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                alpha: 1,
                decay: 0.008 + Math.random() * 0.012
            });
        }

        return {
            particles,
            color,
            originX,
            originY,
            flash: 1,
            lineWidth: 1 + Math.random() * 1.2
        };
    }

    for (let i = 0; i < burstCount; i += 1) {
        setTimeout(() => {
            bursts.push(createBurst());
        }, i * burstDelay);
    }

    let running = true;
    const maxDuration = 3000;
    const start = performance.now();

    function animate(now) {
        const elapsed = now - start;
        ctx.clearRect(0, 0, rect.width, rect.height);

        let alive = false;
        for (const burst of bursts) {
            const [r, g, b] = burst.color;
            ctx.lineWidth = burst.lineWidth;
            ctx.shadowBlur = 6;
            ctx.shadowColor = `rgba(${r}, ${g}, ${b}, 0.6)`;

            if (burst.flash > 0) {
                const radius = 14 + (1 - burst.flash) * 32;
                const gradient = ctx.createRadialGradient(
                    burst.originX,
                    burst.originY,
                    0,
                    burst.originX,
                    burst.originY,
                    radius
                );
                gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${0.8 * burst.flash})`);
                gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(burst.originX, burst.originY, radius, 0, Math.PI * 2);
                ctx.fill();
                burst.flash -= 0.12;
            }

            for (const particle of burst.particles) {
                if (particle.alpha <= 0) {
                    continue;
                }

                alive = true;
                const prevX = particle.x;
                const prevY = particle.y;

                particle.vx *= friction;
                particle.vy = particle.vy * friction + gravity;
                particle.x += particle.vx * 2.8;
                particle.y += particle.vy * 2.8;
                particle.alpha -= particle.decay;

                const alpha = Math.max(particle.alpha, 0);
                ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
                ctx.beginPath();
                ctx.moveTo(prevX, prevY);
                ctx.lineTo(particle.x, particle.y);
                ctx.stroke();
            }
        }

        if ((alive || elapsed < maxDuration) && running) {
            requestAnimationFrame(animate);
        } else {
            confettiLayer.innerHTML = '';
        }
    }

    requestAnimationFrame(animate);

    setTimeout(() => {
        running = false;
    }, maxDuration + 200);
}

function calculateEffectiveSpeed(totalSeconds, wordsRead) {
    if (totalSeconds <= 0 || wordsRead <= 0) {
        return Math.round(baseSpeed);
    }
    return Math.max(1, Math.round((wordsRead * 60) / totalSeconds));
}

function formatDuration(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${pad2(minutes)}:${pad2(seconds)}`;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
}

function clampNumber(value, min, max) {
    if (!Number.isFinite(value)) {
        return min;
    }
    return clamp(value, min, max);
}

function pad2(value) {
    return String(value).padStart(2, '0');
}
