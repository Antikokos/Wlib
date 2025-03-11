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

            // Генерация случайных книг из полученных данных
            const randomBooks = getRandomItems(data.items, 10); // Выбираем 10 книг
            randomBooks.forEach(item => {
                const title = item.volumeInfo.title || 'Без названия';
                const authors = item.volumeInfo.authors ? item.volumeInfo.authors.join(', ') : 'Неизвестные авторы';
                const imageUrl = item.volumeInfo.imageLinks ? item.volumeInfo.imageLinks.thumbnail : 'https://via.placeholder.com/200x240/444';

                const slide = document.createElement('div');
                slide.classList.add('swiper-slide');
                slide.innerHTML = `
                    <div class="book-card">
                        <div class="book-image" style="background-image: url('${imageUrl}');"></div>
                        <div class="book-info">
                            <h3>${title}</h3>
                            <p>Автор: ${authors}</p>
                        </div>
                    </div>
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
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
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


document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-txt');

    // Устанавливаем фокус на поле ввода после загрузки страницы
    searchInput.focus();

    // Обработчик события на изменение значения поля
    searchInput.addEventListener('input', function() {
        if (searchInput.value !== '') {
            searchInput.style.color = 'white';
            searchInput.style.backgroundColor = 'black';
        } else {
            searchInput.style.color = '';
            searchInput.style.backgroundColor = '';
        }
    });

    // Принудительно устанавливаем фокус на поле ввода после автозаполнения
    setTimeout(function() {
        searchInput.focus();
    }, 100);
});







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
const swiper = new Swiper('.mySwiper', {
    allowTouchMove: false,
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