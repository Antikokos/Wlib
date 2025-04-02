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
    const progressText = document.getElementById("progress-text");

    // const currentPages = parseInt(currentPageEl.textContent); // Текущие прочитанные страницы
   
    // const progress = Math.round((currentPages / totalPages) * 100); // Процент прогресса

    // Форматирование описания книги
    if (bookDescription) {
        formatBookDescription(bookDescription);
    }

    // Загрузка сохраненного прогресса и статуса
    const bookId = document.querySelector(".container").getAttribute("data-book-id");
    const savedProgress = localStorage.getItem(`bookProgress_${bookId}`);
    const savedStatus = localStorage.getItem(`bookStatus_${bookId}`);
    const initialProgress = savedProgress ? Math.min(parseInt(savedProgress), totalPages) : 0;

    // Установка начальных значений
    progressSlider.min = 0;
    progressSlider.max = totalPages;
    progressSlider.value = initialProgress;
    pageInput.min = 0;
    pageInput.max = totalPages;
    updateProgress(initialProgress, false);

    if (savedStatus) {
        updateStatusButton(savedStatus);
        if (savedStatus === "read") {
            createSparkles(progressFill);
        }
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
                updateProgress(totalPages, true);
                progressSlider.value = totalPages;
                createSparkles(progressFill);
            }
        });
    });

    progressSlider.addEventListener("input", function() {
        let pages = parseInt(this.value);
        // Ограничиваем значение между min и max
        pages = Math.max(parseInt(this.min), Math.min(parseInt(this.max), pages));
        this.value = pages; // Устанавливаем корректное значение обратно в слайдер
        updateProgress(pages, true);
        sliderTooltip.textContent = pages;
        sliderTooltip.style.left = `${(pages / totalPages) * 100}%`;
    });

    progressSlider.addEventListener("mousemove", function(e) {
        let percent = (e.offsetX / this.offsetWidth) * 100;
        // Ограничиваем процент в пределах 0-100
        percent = Math.max(0, Math.min(100, percent));
        const pages = Math.round((percent / 100) * totalPages);
        sliderTooltip.textContent = pages;
        sliderTooltip.style.left = `${percent}%`;
    });

    progressSlider.addEventListener("mouseenter", function() {
        sliderTooltip.style.opacity = "1";
    });

    progressSlider.addEventListener("mouseleave", function() {
        sliderTooltip.style.opacity = "0";
    });

    decreaseBtn.addEventListener("click", function() {
        let newPages = parseInt(currentPageEl.textContent) - 1;
        newPages = Math.max(0, newPages); // Не позволяем уйти ниже 0
        progressSlider.value = newPages;
        updateProgress(newPages, true);
        sliderTooltip.textContent = newPages;
    });

    increaseBtn.addEventListener("click", function() {
        let newPages = parseInt(currentPageEl.textContent) + 1;
        newPages = Math.min(totalPages, newPages); // Не позволяем превысить totalPages
        progressSlider.value = newPages;
        updateProgress(newPages, true);
        sliderTooltip.textContent = newPages;
    });

    pageInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            updatePagesBtn.click();
        }
    });

    updatePagesBtn.addEventListener("click", function() {
        let pages = parseInt(pageInput.value) || 0;
        pages = Math.max(0, Math.min(totalPages, pages));
        pageInput.value = pages;
        progressSlider.value = pages;
        updateProgress(pages, true);
    });

    function getCSRFToken() {
        return document.getElementById("csrf_token").value;
    }
    
    function saveProgressToServer(pagesRead) {
        const percentage = (pagesRead / totalPages) * 100
        fetch("/update-progress/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // 🔐 Передаём CSRF-токен
            },
            body: JSON.stringify({
                book_id: bookId,
                progress: pagesRead,
                progress_percent: percentage, // Передаём процент прогресса
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                console.log("Прогресс сохранён:", data.progress);
            } else {
                console.error("Ошибка сохранения:", data.message);
            }
        })
        .catch(error => console.error("Ошибка запроса:", error));
    }

    // Функция обновления прогресса
    function updateProgress(pagesRead, showSparkles) {
        pagesRead = Math.max(0, Math.min(totalPages, pagesRead));
        const percentage = (pagesRead / totalPages) * 100;
        const roundedPercentage = Math.round(percentage * 10) / 10;
    
        progressFill.style.width = percentage + "%";
        progressText.textContent = roundedPercentage + "%";
        currentPageEl.textContent = pagesRead;
        pageInput.value = pagesRead;
        progressSlider.value = pagesRead;
    
        localStorage.setItem(`bookProgress_${bookId}`, pagesRead);
        saveProgressToServer(pagesRead); // 📌 Добавлено!
    
        if (showSparkles && pagesRead > 0) {
            createSparkles(progressFill);
        }
    }
    

    // Функция форматирования описания книги
    function formatBookDescription(element) {
        let text = element.textContent.trim();
        text = text.replace(/\s+/g, ' ');
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
        if (!sparklesContainer) return;

        sparklesContainer.innerHTML = "";
        const width = parseFloat(container.style.width) || 0;

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

    function updateBookStatus(status) {
        const currentPages = parseInt(currentPageEl.textContent);
        const totalPages = parseInt(document.getElementById("total-pages").textContent) || 1;
        const progress = Math.round((currentPages / totalPages) * 100);
    
        fetch("/update_book_status/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),  // Используем CSRF-токен из hidden input
            },
            body: JSON.stringify({
                book_id: bookId,
                status: status,
                progress: status === 'read' ? totalPages : currentPages,
                current_page: status === 'read' ? totalPages : currentPages, // Передаем текущую страницу
                progress_percent: status === 'read' ? 100 : progress // Передаем прогресс в процентах
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Книга добавлена в "${getStatusName(status)}"`);
                // Обновляем localStorage
                localStorage.setItem(`bookStatus_${bookId}`, status);
                localStorage.setItem(`bookProgress_${bookId}`, status === 'read' ? totalPages : currentPages);
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
});

// Стили для уведомлений
const notificationStyle = document.createElement("style");
notificationStyle.textContent = `
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
document.head.appendChild(notificationStyle);