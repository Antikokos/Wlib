const genres = ['fantasy', 'detective', 'manga', 'romance'];

// Функция для получения случайных книг
function fetchRandomBooks(genre, containerClass) {
    const url = `https://www.googleapis.com/books/v1/volumes?q=subject:${genre}&maxResults=40`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const carousel = $(`.${containerClass}-carousel`);
            carousel.empty(); // Очистка контейнера перед загрузкой новых книг

            // Генерация случайных книг из полученных данных
            const randomBooks = getRandomItems(data.items, 40);
            randomBooks.forEach(item => {
                const title = item.volumeInfo.title || 'Без названия';
                const author = item.volumeInfo.authors ? item.volumeInfo.authors.join(', ') : 'Неизвестный автор';
                const imageUrl = item.volumeInfo.imageLinks ? item.volumeInfo.imageLinks.thumbnail : null;
                const bookId = item.id; // ID книги для ссылки

                // Пропускаем книги без изображений
                if (!imageUrl) return;

                // Создаем карточку книги с правильной ссылкой
                const bookCard = `
                    <div class="book-card">
                        <a href="/book/${bookId}"> <!-- Исправленный URL -->
                            <div class="book-image" style="background-image: url('${imageUrl}');"></div>
                            <div class="book-info">
                                <h3>${title}</h3>
                                <p>Автор: ${author}</p>
                            </div>
                        </a>
                    </div>
                `;
                carousel.append(bookCard);
            });

            // Инициализация Slick Carousel
            carousel.slick({
                slidesToShow: 5, // Показываем 5 книг в ряду
                slidesToScroll: 2, // Прокручиваем по 2 книги
                infinite: true, // Бесконечная прокрутка
                prevArrow: "<button type='button' class='slick-prev'>&#10094;</button>", // Стрелка "назад"
                nextArrow: "<button type='button' class='slick-next'>&#10095;</button>", // Стрелка "вперед"
            });
        })
        .catch(error => console.error('Ошибка при загрузке книг:', error));
}

// Функция для получения случайных элементов
function getRandomItems(arr, count) {
    const shuffled = arr.slice(0); // Копируем массив
    let i = arr.length, temp, randomIndex;

    while (i !== 0) {
        randomIndex = Math.floor(Math.random() * i);
        i--;
        temp = shuffled[i];
        shuffled[i] = shuffled[randomIndex];
        shuffled[randomIndex] = temp;
    }

    return shuffled.slice(0, count);
}

// Загружаем книги для каждого жанра
genres.forEach(genre => {
    fetchRandomBooks(genre, genre);
});
