document.addEventListener("DOMContentLoaded", function() {
    // Инициализация элементов
    const statusMainButton = document.getElementById("status-main-button");
    const statusMainText = document.getElementById("status-main-text");
    const statusButtons = document.getElementById("status-buttons");
    const progressSlider = document.getElementById("progress-slider");
    const sliderTooltip = document.getElementById("slider-tooltip");
    const decreaseBtn = document.getElementById("decrease-btn");
    const increaseBtn = document.getElementById("increase-btn");
    const pageInput = document.getElementById("page-input");
    const updatePagesBtn = document.getElementById("update-pages");
    const currentPageEl = document.getElementById("current-page");
    const totalPages = parseInt(document.getElementById("total-pages").textContent) || 1;
    const progressFill = document.getElementById("progress-fill");
    const bookDescription = document.getElementById("book-description");

    // Форматирование описания книги
    if (bookDescription) {
        formatBookDescription(bookDescription);
    }

    // Загрузка сохраненного прогресса и статуса
    const bookId = document.querySelector(".container").getAttribute("data-book-id");
    const savedProgress = localStorage.getItem(`bookProgress_${bookId}`);
    const savedStatus = localStorage.getItem(`bookStatus_${bookId}`);
    const initialProgress = savedProgress ? parseInt(savedProgress) : 0;

    // Установка начальных значений
    updateProgress(initialProgress);
    progressSlider.value = initialProgress;
    pageInput.max = totalPages;

    if (savedStatus) {
        updateStatusButton(savedStatus);
        createSparkles(progressFill);
    }

    // Обработчики событий
    statusMainButton.addEventListener("click", function(e) {
        e.stopPropagation();
        statusButtons.style.display = statusButtons.style.display === "flex" ? "none" : "flex";
    });

    document.addEventListener("click", function() {
        statusButtons.style.display = "none";
    });

    document.querySelectorAll(".status-btn").forEach(button => {
        button.addEventListener("click", function(e) {
            e.stopPropagation();
            const status = this.getAttribute("data-status");
            updateBookStatus(status);
            updateStatusButton(status);
            statusButtons.style.display = "none";

            if (status === "read") {
                updateProgress(100);
                progressSlider.value = 100;
                createSparkles(progressFill);
            }
        });
    });

    progressSlider.addEventListener("input", function() {
        const value = this.value;
        updateProgress(value);
        createSparkles(progressFill);
        sliderTooltip.textContent = `${value}%`;
        sliderTooltip.style.left = `${(value / this.max) * 100}%`;
    });

    progressSlider.addEventListener("mousemove", function(e) {
        sliderTooltip.style.left = `${(e.offsetX / this.offsetWidth) * 100}%`;
    });

    progressSlider.addEventListener("mouseenter", function() {
        sliderTooltip.style.opacity = "1";
    });

    progressSlider.addEventListener("mouseleave", function() {
        sliderTooltip.style.opacity = "0";
    });

    decreaseBtn.addEventListener("click", function() {
        let newValue = parseInt(progressSlider.value) - 5;
        if (newValue < 0) newValue = 0;
        progressSlider.value = newValue;
        updateProgress(newValue);
        sliderTooltip.textContent = `${newValue}%`;
        createSparkles(progressFill);
    });

    increaseBtn.addEventListener("click", function() {
        let newValue = parseInt(progressSlider.value) + 5;
        if (newValue > 100) newValue = 100;
        progressSlider.value = newValue;
        updateProgress(newValue);
        sliderTooltip.textContent = `${newValue}%`;
        createSparkles(progressFill);
    });

    updatePagesBtn.addEventListener("click", function() {
        const pages = parseInt(pageInput.value) || 0;
        if (pages < 0) {
            pageInput.value = 0;
            updateProgress(0);
        } else if (pages > totalPages) {
            pageInput.value = totalPages;
            updateProgress(100);
        } else {
            const percentage = Math.round((pages / totalPages) * 100);
            updateProgress(percentage);
            progressSlider.value = percentage;
        }
        createSparkles(progressFill);
    });

    // Функция форматирования описания книги
    function formatBookDescription(element) {
        let text = element.textContent.trim();

        // Удаляем лишние пробелы и переносы
        text = text.replace(/\s+/g, ' ');

        // Разбиваем на абзацы по точкам (кроме сокращений)
        text = text.replace(/([^A-ZА-Я]\.)\s+/g, '$1\n\n');
        text = text.replace(/\n+/g, '\n').trim();

        const paragraphs = text.split('\n').filter(p => p.length > 0);
        let formattedText = '';

        paragraphs.forEach((para, index) => {
            if (index === 0) {
                formattedText += `<p class="first-para">${para}</p>`;
            } else {
                formattedText += `<p>${para}</p>`;
            }
        });

        element.innerHTML = formattedText;
    }

    function updateProgress(percentage) {
        percentage = Math.min(100, Math.max(0, percentage));
        const pagesRead = Math.round((percentage / 100) * totalPages);

        progressFill.style.width = percentage + "%";
        document.getElementById("progress-text").textContent = percentage + "%";
        currentPageEl.textContent = pagesRead;
        pageInput.value = pagesRead;

        localStorage.setItem(`bookProgress_${bookId}`, percentage);
    }

    function updateStatusButton(status) {
        statusMainButton.classList.remove("reading", "want-to-read", "read");

        switch(status) {
            case "reading":
                statusMainButton.classList.add("reading");
                statusMainText.textContent = "Читаю";
                break;
            case "want-to-read":
                statusMainButton.classList.add("want-to-read");
                statusMainText.textContent = "В планах";
                break;
            case "read":
                statusMainButton.classList.add("read");
                statusMainText.textContent = "Прочитано";
                break;
            default:
                statusMainText.textContent = "Добавить в мои книги";
        }

        localStorage.setItem(`bookStatus_${bookId}`, status);
    }

    function createSparkles(container) {
        const sparklesContainer = container.querySelector(".progress-bar-sparkles");
        if (sparklesContainer) {
            sparklesContainer.innerHTML = "";

            const width = parseInt(container.style.width) || 0;
            if (width > 0) {
                for (let i = 0; i < 5; i++) {
                    const sparkle = document.createElement("div");
                    sparkle.className = "sparkle";
                    sparkle.style.left = `${Math.random() * width}%`;
                    sparkle.style.top = `${Math.random() * 100}%`;
                    sparkle.style.width = `${Math.random() * 4 + 2}px`;
                    sparkle.style.height = sparkle.style.width;
                    sparkle.style.animationDelay = `${Math.random() * 2}s`;
                    sparklesContainer.appendChild(sparkle);
                }
            }
        }
    }

    function updateBookStatus(status) {
        fetch("/update_book_status/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                book_id: bookId,
                status: status,
                progress: progressSlider.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Книга добавлена в "${getStatusName(status)}"`);
            } else {
                showNotification("Ошибка: " + data.message, true);
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
            showNotification("Произошла ошибка", true);
        });
    }

    function getStatusName(status) {
        const names = {
            "reading": "Читаю",
            "want-to-read": "В планах",
            "read": "Прочитано"
        };
        return names[status] || status;
    }

    function showNotification(message, isError = false) {
        const notification = document.createElement("div");
        notification.className = `notification ${isError ? "error" : "success"}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add("show"), 10);
        setTimeout(() => {
            notification.classList.remove("show");
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

// Стили для уведомлений
const style = document.createElement("style");
style.textContent = `
.notification {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    padding: 14px 28px;
    border-radius: 8px;
    background: #2ecc71;
    color: white;
    font-size: 16px;
    font-weight: 500;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    opacity: 0;
    transition: opacity 0.3s ease, transform 0.3s ease;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 10px;
}

.notification.error {
    background: #e74c3c;
}

.notification.show {
    opacity: 1;
    transform: translateX(-50%) translateY(-10px);
}

.notification::before {
    font-family: "Font Awesome 6 Free";
    font-weight: 900;
}

.notification.success::before {
    content: "\\f00c";
}

.notification.error::before {
    content: "\\f06a";
}
`;
document.head.appendChild(style);