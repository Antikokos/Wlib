// Инициализация данных книги
function fetchBookData() {
    const bookId = "{{ book.id }}"; // ID книги берется из шаблона
    const apiUrl = `https://www.googleapis.com/books/v1/volumes/${bookId}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const book = data.volumeInfo;
            document.getElementById('book-title').innerText = book.title || 'Без названия';
            document.getElementById('book-author').innerText = `Автор: ${book.authors ? book.authors.join(', ') : 'Неизвестно'}`;
            document.getElementById('book-description').innerText = book.description || 'Описание отсутствует';
            document.getElementById('book-cover').src = book.imageLinks?.thumbnail || 'default-book-image.jpg';
            document.getElementById('book-publisher').innerText = `Издательство: ${book.publisher || 'Неизвестно'}`;
            document.getElementById('book-year').innerText = `Год: ${book.publishedDate ? book.publishedDate.slice(0, 4) : 'Неизвестно'}`;
            document.getElementById('book-pages').innerText = `Страниц: ${book.pageCount || 'Неизвестно'}`;
            updateProgress(0); // Инициализация прогресса на 0%
        })
        .catch(error => console.error('Ошибка загрузки данных книги:', error));
}

// Переключение видимости кнопок статуса
function toggleStatusButtons() {
    const buttons = document.getElementById('status-buttons');
    buttons.style.display = buttons.style.display === 'block' ? 'none' : 'block';
}

// Обновление статуса книги (добавление в профиль пользователя)
function updateStatus(status) {
    const bookId = "{{ book.id }}"; // ID книги берется из шаблона

    console.log('Отправка запроса:', { book_id: bookId, status: status });

    fetch(`/update_book_status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // CSRF-токен для защиты
        },
        body: JSON.stringify({
            book_id: bookId,
            status: status
        })
    })
    .then(response => {
        if (!response.ok) {
            console.error('Ошибка HTTP:', response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Ответ сервера:', data);
        if (data.success) {
            alert('Книга успешно добавлена!');
        } else {
            alert('Ошибка при добавлении книги.');
        }
    })
    .catch(error => console.error('Ошибка при отправке запроса:', error));
}

// Функция для получения CSRF-токена из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Обновление прогресса чтения
function updateProgress(percentage) {
    const progressBar = document.getElementById('progress-fill');
    const progressText = document.getElementById('book-progress-text');
    progressBar.style.width = percentage + '%';
    progressText.innerText = percentage + '%';
}

// Загружаем данные книги при загрузке страницы
window.onload = fetchBookData;