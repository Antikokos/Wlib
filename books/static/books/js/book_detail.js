const bookId = 'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA'

        function fetchBookData() {
            const apiUrl = `https://www.googleapis.com/books/v1/volumes/${bookId}`;
            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    const book = data.volumeInfo;
                    document.getElementById('book-title').innerText = book.title;
                    document.getElementById('book-author').innerText = `Автор: ${book.authors ? book.authors.join(', ') : 'Неизвестно'}`;
                    document.getElementById('book-description').innerText = book.description || 'Описание отсутствует';
                    document.getElementById('book-cover').src = book.imageLinks ? book.imageLinks.thumbnail : 'default-book-image.jpg';
                    document.getElementById('book-publisher').innerText = `Издательство: ${book.publisher || 'Неизвестно'}`;
                    document.getElementById('book-year').innerText = `Год: ${book.publishedDate ? book.publishedDate.slice(0, 4) : 'Неизвестно'}`;
                    document.getElementById('book-pages').innerText = `Страниц: ${book.pageCount || 'Неизвестно'}`;
                    updateProgress(0); // Инициализация прогресса на 0%
                })
                .catch(error => console.error('Ошибка загрузки данных книги:', error));
        }

        function updateStatus(status) {
            alert(`Статус книги обновлен на: ${status}`);
            // Здесь можно обновить статус книги в базе данных пользователя
        }

        function toggleStatusButtons() {
            const statusButtons = document.getElementById('status-buttons');
            if (statusButtons.style.display === 'none' || statusButtons.style.display === '') {
                statusButtons.style.display = 'flex';
            } else {
                statusButtons.style.display = 'none';
            }
        }

        // Обновление прогресса
        function updateProgress(percentage) {
            const progressBar = document.getElementById('progress-fill');
            const progressText = document.getElementById('book-progress-text');
            progressBar.style.width = percentage + '%';
            progressText.innerText = percentage + '%';
        }

        // Загружаем данные книги при загрузке страницы
        window.onload = fetchBookData;