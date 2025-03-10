const genres = ['fantasy', 'detective', 'manga', 'romance'];

// Функция для получения случайных книг
function fetchRandomBooks(genre, containerId) {
    const url = `https://www.googleapis.com/books/v1/volumes?q=subject:${genre}&maxResults=10`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById(containerId);
            const swiperWrapper = container.querySelector('.swiper-wrapper');
            swiperWrapper.innerHTML = ''; // Очистка контейнера перед загрузкой новых книг

            if (!data.items) {
                console.error('Нет данных для жанра:', genre);
                swiperWrapper.innerHTML = `<p>Книги не найдены для жанра: ${genre}</p>`;
                return;
            }

            // Генерация случайных книг из полученных данных
            const randomBooks = getRandomItems(data.items, 10); // Выбираем 10 книг
            randomBooks.forEach(item => {
                const title = item.volumeInfo.title || 'Без названия';
                const authors = item.volumeInfo.authors ? item.volumeInfo.authors.join(', ') : 'Неизвестные авторы';
                const imageUrl = item.volumeInfo.imageLinks ? item.volumeInfo.imageLinks.thumbnail : 'https://via.placeholder.com/200x240/444';
                const publisher = item.volumeInfo.publisher || 'Неизвестный издатель';
                const pageCount = item.volumeInfo.pageCount || 'Неизвестно';
                const publishedDate = item.volumeInfo.publishedDate || 'Неизвестно';

                const slide = document.createElement('div');
                slide.classList.add('swiper-slide');
                slide.innerHTML = `
                    <a href="{% url 'book_detail' %}"> <!-- Добавьте сюда ID книги, если нужно -->
                        <div class="book-card">
                            <div class="book-image" style="background-image: url('${imageUrl}');"></div>
                            <div class="book-info">
                                <h3>${title}</h3>
                                <p>Автор: ${authors}</p>
                                <p>Издатель: ${publisher}</p>
                                <p>Кол-во страниц: ${pageCount}</p>
                                <p>Год выхода: ${publishedDate}</p>
                            </div>
                        </div>
                    </a>
                `;
                swiperWrapper.appendChild(slide);
            });

            // Инициализация Swiper после добавления слайдов
            new Swiper(`#${containerId}`, {
                slidesPerView: 5, // Количество видимых слайдов
                spaceBetween: 10, // Расстояние между слайдами
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: `.swiper-button-next`,
                    prevEl: `.swiper-button-prev`,
                },
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке книг:', error);
            const container = document.getElementById(containerId);
            container.innerHTML = `<p>Ошибка при загрузке книг для жанра: ${genre}</p>`;
        });
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

// Функция сортировки книг (если нужно)
function sortBooks() {
    const sortOption = document.getElementById("sortOption").value;
    const books = Array.from(document.querySelectorAll('.book-card'));

    if (sortOption === "pages") {
        books.sort((a, b) => {
            const aPages = parseInt(a.querySelector('.book-info p:nth-child(3)').textContent.split(': ')[1]);
            const bPages = parseInt(b.querySelector('.book-info p:nth-child(3)').textContent.split(': ')[1]);
            return bPages - aPages;
        });
    } else if (sortOption === "year") {
        books.sort((a, b) => {
            const aYear = parseInt(a.querySelector('.book-info p:nth-child(4)').textContent.split(': ')[1]);
            const bYear = parseInt(b.querySelector('.book-info p:nth-child(4)').textContent.split(': ')[1]);
            return bYear - aYear;
        });
    }

    const bookContainer = document.getElementById('book-container');
    bookContainer.innerHTML = '';
    books.forEach(book => bookContainer.appendChild(book));
}

// Инициализация Swiper для каждого слайдера
genres.forEach(genre => {
    new Swiper(`#${genre}`, {
        slidesPerView: 4,
        spaceBetween: 10,
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
    });
});