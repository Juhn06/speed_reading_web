/**
 * Reader Logic
 * Xử lý logic đọc từng từ
 */

// Get data from localStorage
let words = JSON.parse(localStorage.getItem('words')) || [];
let speed = parseInt(localStorage.getItem('speed')) || 200;
let filename = localStorage.getItem('filename') || 'Tài liệu';
let docId = localStorage.getItem('doc_id');
let totalWords = parseInt(localStorage.getItem('total_words')) || words.length;

// State variables
let currentIndex = 0;
let intervalId = null;
let timerInterval = null;
let startTime = null;
let isPaused = false;
let isRunning = false;
let pausedTime = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (words.length === 0) {
        document.getElementById('wordDisplay').textContent =
            'Không có dữ liệu. Vui lòng quay lại trang chủ!';
        return;
    }

    // Display initial info
    document.getElementById('total').textContent = totalWords;
    document.getElementById('currentSpeed').textContent = speed;

    // Update button state
    updateButton('play');
});

// Calculate interval time between words
const intervalTime = (60 / speed) * 1000;

// Toggle Play/Pause
function togglePlayPause() {
    if (words.length === 0) {
        alert('⚠️ Không có dữ liệu. Vui lòng quay lại trang chủ!');
        return;
    }

    if (isRunning) {
        pauseReading();
    } else {
        startReading();
    }
}

// Start reading
function startReading() {
    // First time start
    if (!startTime) {
        startTime = Date.now();
        startTimer();
    }

    // Resume from pause
    if (isPaused) {
        isPaused = false;
        startTime = Date.now() - pausedTime;
    }

    isRunning = true;

    // Clear old interval
    if (intervalId) {
        clearInterval(intervalId);
    }

    // Start displaying words
    intervalId = setInterval(() => {
        if (currentIndex < words.length) {
            displayWord(words[currentIndex]);
            currentIndex++;
            updateProgress();
            updatePercentage();
        } else {
            finishReading();
        }
    }, intervalTime);

    // Update button
    updateButton('pause');
}

// Display word
function displayWord(word) {
    document.getElementById('wordDisplay').textContent = word;
}

// Pause reading
function pauseReading() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }

    isRunning = false;
    isPaused = true;

    // Save elapsed time
    if (startTime) {
        pausedTime = Date.now() - startTime;
    }

    // Update button
    updateButton('resume');
}

// Reset reading
function resetReading() {
    // Clear intervals
    clearInterval(intervalId);
    clearInterval(timerInterval);

    // Reset state
    intervalId = null;
    timerInterval = null;
    currentIndex = 0;
    startTime = null;
    isPaused = false;
    isRunning = false;
    pausedTime = 0;

    // Reset display
    document.getElementById('wordDisplay').textContent = 'Nhấn Play để bắt đầu';
    document.getElementById('timer').textContent = '00:00';
    document.getElementById('progress').textContent = '0';
    document.getElementById('percentage').textContent = '0';

    // Update button
    updateButton('play');
}

// Update progress
function updateProgress() {
    document.getElementById('progress').textContent = currentIndex;
}

// Update percentage
function updatePercentage() {
    const percent = Math.round((currentIndex / totalWords) * 100);
    document.getElementById('percentage').textContent = percent;
}

// Start timer
function startTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    timerInterval = setInterval(() => {
        if (isRunning && startTime) {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;

            document.getElementById('timer').textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

// Finish reading
async function finishReading() {
    clearInterval(intervalId);
    clearInterval(timerInterval);

    const totalTime = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(totalTime / 60);
    const seconds = totalTime % 60;

    // Save session to backend
    try {
        await API.saveSession({
            doc_id: docId,
            filename: filename,
            total_words: totalWords,
            words_read: currentIndex,
            speed: speed,
            duration: totalTime,
            completed: currentIndex === totalWords
        });
    } catch (error) {
        console.error('Error saving session:', error);
    }

    // Show completion message
    alert(
        `🎉 Hoàn thành!\n\n` +
        `📚 Tổng: ${totalWords} từ\n` +
        `📖 Đã đọc: ${currentIndex} từ\n` +
        `⏱️ Thời gian: ${minutes}:${seconds.toString().padStart(2, '0')}\n` +
        `🚀 Tốc độ: ${speed} từ/phút\n` +
        `✅ Hoàn thành: ${Math.round((currentIndex / totalWords) * 100)}%`
    );

    // Reset or go back
    if (confirm('Bạn muốn đọc lại tài liệu này?')) {
        resetReading();
    } else {
        goBack();
    }
}

// Update button state
function updateButton(state) {
    const btn = document.getElementById('playPauseBtn');

    if (!btn) {
        console.error('Button not found!');
        return;
    }

    if (state === 'play') {
        btn.innerHTML = '<i class="fas fa-play"></i><span>Play</span>';
        btn.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
    } else if (state === 'pause') {
        btn.innerHTML = '<i class="fas fa-pause"></i><span>Pause</span>';
        btn.style.background = 'linear-gradient(135deg, #f59e0b, #d97706)';
    } else if (state === 'resume') {
        btn.innerHTML = '<i class="fas fa-play"></i><span>Resume</span>';
        btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    }
}

// Go back to dashboard
function goBack() {
    if (confirm('Bạn có chắc muốn thoát?Tiến độ hiện tại sẽ được lưu.')) {
        // Save current progress before leaving
        if (startTime && currentIndex > 0) {
            const totalTime = Math.floor((Date.now() - startTime) / 1000);

            API.saveSession({
                doc_id: docId,
                filename: filename,
                total_words: totalWords,
                words_read: currentIndex,
                speed: speed,
                duration: totalTime,
                completed: false
            }).catch((error) => {
                console.error('Error saving session:', error);
            });
        }

        window.location.href = '/user/dashboard';
    }
}
