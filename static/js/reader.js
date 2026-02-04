// Lấy dữ liệu từ localStorage
let words = JSON.parse(localStorage.getItem('words')) || [];
let speed = parseInt(localStorage.getItem('speed')) || 200;

let currentIndex = 0;
let intervalId = null;
let startTime = null;
let isPaused = false;
let timerInterval = null;
let pausedTime = 0; // Lưu thời gian đã pause

// Hiển thị thông tin ban đầu
document.getElementById('total').textContent = words.length;
document.getElementById('currentSpeed').textContent = speed;

// Tính khoảng thời gian giữa các từ (miliseconds)
let intervalTime = (60 / speed) * 1000;

// Bắt đầu đọc
function startReading() {
    if (words.length === 0) {
        alert('⚠️ Không có dữ liệu. Vui lòng quay lại trang chủ!');
        return;
    }

    // Nếu chưa bắt đầu lần nào
    if (!startTime) {
        startTime = Date.now();
        startTimer();
    }

    // Nếu đang pause, tiếp tục từ vị trí cũ
    if (isPaused) {
        isPaused = false;
        startTime = Date.now() - pausedTime; // Điều chỉnh lại thời gian
    }

    // Clear interval cũ nếu có
    if (intervalId) {
        clearInterval(intervalId);
    }

    intervalId = setInterval(() => {
        if (currentIndex < words.length) {
            displayWord(words[currentIndex]);
            currentIndex++;
            updateProgress();
        } else {
            finishReading();
        }
    }, intervalTime);
}

// Hiển thị từ
function displayWord(word) {
    document.getElementById('wordDisplay').textContent = word;
}

// Tạm dừng
function pauseReading() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    isPaused = true;

    // Lưu thời gian đã chạy
    if (startTime) {
        pausedTime = Date.now() - startTime;
    }
}

// Reset
function resetReading() {
    clearInterval(intervalId);
    clearInterval(timerInterval);
    intervalId = null;
    timerInterval = null;
    currentIndex = 0;
    startTime = null;
    isPaused = false;
    pausedTime = 0;

    document.getElementById('wordDisplay').textContent = 'Nhấn Play để bắt đầu';
    document.getElementById('timer').textContent = '00:00';
    document.getElementById('progress').textContent = '0';
}

// Cập nhật tiến độ
function updateProgress() {
    document.getElementById('progress').textContent = currentIndex;
}

// Cập nhật thời gian
function startTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    timerInterval = setInterval(() => {
        if (!isPaused && startTime) {
            let elapsed = Math.floor((Date.now() - startTime) / 1000);
            let minutes = Math.floor(elapsed / 60);
            let seconds = elapsed % 60;

            document.getElementById('timer').textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

// Hoàn thành
function finishReading() {
    clearInterval(intervalId);
    clearInterval(timerInterval);

    let totalTime = Math.floor((Date.now() - startTime) / 1000);
    let minutes = Math.floor(totalTime / 60);
    let seconds = totalTime % 60;

    alert(`🎉 Hoàn thành!\n\n` +
          `📚 Tổng: ${words.length} từ\n` +
          `⏱️ Thời gian: ${minutes}:${seconds.toString().padStart(2, '0')}\n` +
          `🚀 Tốc độ: ${speed} từ/phút`);
}

// Quay lại trang chủ
function goBack() {
    window.location.href = '/';
}