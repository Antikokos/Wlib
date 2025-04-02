document.addEventListener("DOMContentLoaded", function() {
    // Проверяем авторизацию пользователя
    const container = document.querySelector(".container");
    if (!container) return;

    const isAuthenticated = container.getAttribute("data-is-authenticated") === "true";
    const bookId = container.getAttribute("data-book-id");

    if (!isAuthenticated) {
        // Скрываем элементы управления для неавторизованных пользователей
        const controls = document.querySelectorAll(".book-status-container, .reading-progress");
        controls.forEach(el => el.style.display = "none");
        return;
    }

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
    const totalPagesEl = document.getElementById("total-pages");
    const totalPages = totalPagesEl ? parseInt(totalPagesEl.textContent) || 1 : 1;
    const progressFill = document.getElementById("progress-fill");
    const bookDescription = document.getElementById("book-description");
    const progressText = document.getElementById("progress-text");

    // Проверяем, что все необходимые элементы существуют
    if (!statusMainButton || !progressSlider || !progressFill) {
        console.error("Не найдены необходимые элементы управления");
        return;
    }

    // Форматирование описания книги
    if (bookDescription) {
        formatBookDescription(bookDescription);
    }

    // Инициализация слайдера
    function initSlider() {
        progressSlider.min = 0;
        progressSlider.max = totalPages;
        progressSlider.step = 1;
        progressSlider.style.setProperty('--progress-percent', '0%');

        progressSlider.addEventListener("input", function() {
            const pages = Math.min(totalPages, Math.max(0, parseInt(this.value)));
            updateProgress(pages, false); // Не сохраняем на сервер
            updateSliderTooltip(pages);
            animateUpdateButton();
        });

        progressSlider.addEventListener("change", function() {
            animateUpdateButton();
        });
    }

    // Обновление подсказки слайдера
    function updateSliderTooltip(pages) {
        if (!sliderTooltip) return;
        const thumbPosition = (pages / totalPages) * 100;
        sliderTooltip.textContent = `${pages} стр.`;
        sliderTooltip.style.left = `calc(${thumbPosition}% + (${8 - thumbPosition * 0.16}px))`;
    }

    // Анимация кнопки сохранения
    function animateUpdateButton() {
        if (!updatePagesBtn) return;

        // Добавляем класс для анимации
        updatePagesBtn.classList.add('pulse');

        // Удаляем класс через время, чтобы анимация повторялась
        setTimeout(() => {
            updatePagesBtn.classList.remove('pulse');
        }, 1000);
    }

    // Загрузка данных с сервера
    loadBookData();

    // Обработчики событий
    statusMainButton?.addEventListener("click", function(e) {
        e.stopPropagation();
        statusButtons.style.display = statusButtons.style.display === "flex" ? "none" : "flex";
    });

    document.addEventListener("click", function() {
        if (statusButtons) statusButtons.style.display = "none";
    });

    document.querySelectorAll(".status-btn").forEach(button => {
        button.addEventListener("click", function(e) {
            e.stopPropagation();
            const status = this.getAttribute("data-status");
            updateBookStatus(status);
            if (statusButtons) statusButtons.style.display = "none";

            if (status === "read") {
                updateProgress(totalPages, true);
                if (progressSlider) progressSlider.value = totalPages;
                createSparkles(progressFill);
                showNotification("Книга отмечена как прочитанная");
            }
        });
    });

    if (decreaseBtn) {
        decreaseBtn.addEventListener("click", function() {
            let newPages = parseInt(currentPageEl.textContent) - 1;
            newPages = Math.max(0, newPages);
            if (progressSlider) progressSlider.value = newPages;
            updateProgress(newPages, false);
            animateUpdateButton();
        });
    }

    if (increaseBtn) {
        increaseBtn.addEventListener("click", function() {
            let newPages = parseInt(currentPageEl.textContent) + 1;
            newPages = Math.min(totalPages, newPages);
            if (progressSlider) progressSlider.value = newPages;
            updateProgress(newPages, false);
            animateUpdateButton();
        });
    }

    if (pageInput) {
        pageInput.addEventListener("input", function() {
            animateUpdateButton();
        });

        pageInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                updatePages();
            }
        });
    }

    if (updatePagesBtn) {
        updatePagesBtn.addEventListener("click", updatePages);
    }

    function updatePages() {
        let pages = parseInt(pageInput.value) || 0;
        pages = Math.max(0, Math.min(totalPages, pages));
        updateProgress(pages, true);
        showNotification("Прогресс обновлен");
    }

    // Функция загрузки данных книги
    function loadBookData() {
        fetch(`/get_book_status/?book_id=${bookId}`, {
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            if (data.exists) {
                updateStatusButton(data.status);
                updateProgress(data.progress, false);

                if (data.status === "read" && progressFill) {
                    createSparkles(progressFill);
                }
            } else {
                updateStatusButton("");
                updateProgress(0, false);
            }
            initSlider();
        })
        .catch(error => {
            console.error("Ошибка загрузки данных:", error);
            showNotification("Ошибка загрузки данных книги", true);
        });
    }

    // Функция обновления прогресса
    function updateProgress(pagesRead, saveToServer) {
        pagesRead = Math.max(0, Math.min(totalPages, pagesRead));
        const percentage = (pagesRead / totalPages) * 100;
        const roundedPercentage = Math.round(percentage * 10) / 10;

        progressFill.style.width = percentage + "%";
        progressText.textContent = roundedPercentage + "%";
        currentPageEl.textContent = pagesRead;
        if (pageInput) pageInput.value = pagesRead;
        if (progressSlider) {
            progressSlider.value = pagesRead;
            progressSlider.style.setProperty('--progress-percent', `${percentage}%`);
        }
        updateSliderTooltip(pagesRead);

        if (saveToServer) {
            saveProgressToServer(pagesRead);
        }

        if (saveToServer && pagesRead > 0) {
            createSparkles(progressFill);
        }
    }

    // Функция сохранения прогресса на сервере
    function saveProgressToServer(pagesRead) {
        const percentage = (pagesRead / totalPages) * 100;
        fetch("/update-progress/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                book_id: bookId,
                progress: pagesRead,
                progress_percent: percentage,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== "success") {
                console.error("Ошибка сохранения:", data.message);
                showNotification("Ошибка сохранения прогресса", true);
            }
        })
        .catch(error => {
            console.error("Ошибка запроса:", error);
            showNotification("Ошибка соединения с сервером", true);
        });
    }

    // Функция обновления статуса книги
    function updateBookStatus(status) {
        const currentPages = parseInt(currentPageEl.textContent);
        const progress = Math.round((currentPages / totalPages) * 100);

        fetch("/update_book_status/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                book_id: bookId,
                status: status,
                progress: status === 'read' ? totalPages : currentPages,
                progress_percent: status === 'read' ? 100 : progress
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatusButton(status);
                showNotification(`Книга добавлена в "${getStatusName(status)}"`);

                if (status === 'read') {
                    updateProgress(totalPages, false);
                    createSparkles(progressFill);
                }
            } else {
                showNotification("Ошибка: " + data.message, true);
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
            showNotification("Произошла ошибка", true);
        });
    }

    // Вспомогательные функции
    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
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
    }

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