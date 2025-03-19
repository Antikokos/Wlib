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
            searchInput.style.backgroundColor = '#1d1f21';
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





function getTextValue(book, keyword) {
    const textElement = [...book.querySelectorAll('.book-info p')]
        .find(p => p.textContent.includes(keyword));

    if (!textElement) {
        console.warn(`Не найдено поле "${keyword}" в`, book);
        return 0;
    }

    let value = textElement.textContent.split(": ")[1]; // Извлекаем текст после ": "
    
    // Для сортировки по году, берем первые 4 символа (год)
    if (keyword === "Год выхода") {
        if (value.length >= 10) {
            // Если есть полный формат даты (например "2021-07-01"), сохраняем полную дату
            return value;  // Возвращаем как строку для дальнейшего сравнения по полному формату
        } else if (value.length >= 4) {
            // Если это только год, берем первые 4 символа
            return value.slice(0, 4);  // Только год
        }
    }
    
    // Для других случаев (например "Кол-во страниц") преобразуем в число
    value = parseInt(value.replace(/\D/g, ''), 10);
    console.log(`Найдено: "${keyword}" → ${value}`);
    return value || 0;
}

function sortBooks() {
    const sortOption = document.getElementById("sortOption").value;
    const books = Array.from(document.querySelectorAll('.book-container a')); // Берем <a>, а не .book-card

    books.sort((a, b) => {
        if (sortOption === "pages") {
            return getTextValue(b, "Кол-во страниц") - getTextValue(a, "Кол-во страниц");
        } else if (sortOption === "year") {
            const valueA = getTextValue(a, "Год выхода");
            const valueB = getTextValue(b, "Год выхода");

            // Если значения полные даты, то сортируем их как строки
            if (valueA.length === 10 && valueB.length === 10) {
                return valueB.localeCompare(valueA); // Сортируем по дате (год-месяц-день)
            }

            // Если это только годы, сортируем их как числа
            return valueB - valueA; // Сортируем по году
        }
    });

    const bookContainer = document.getElementById('book-container');
    const fragment = document.createDocumentFragment(); 

    books.forEach(book => fragment.appendChild(book)); // Вставляем <a>, а не .book-card

    bookContainer.innerHTML = ''; 
    bookContainer.appendChild(fragment); 
}


let isReversed = false;

function reverseBooks() {
    isReversed = !isReversed; // Переключаем флаг реверса
    const bookContainer = document.getElementById('book-container');
    const books = Array.from(bookContainer.children).reverse();
    
    updateBookList(books);

    // Добавляем/убираем класс поворота
    document.querySelector('.reverse-button').classList.toggle('rotated', isReversed);
}

function updateBookList(books) {
    const bookContainer = document.getElementById('book-container');
    const fragment = document.createDocumentFragment();

    books.forEach(book => fragment.appendChild(book));
    
    bookContainer.innerHTML = ''; 
    bookContainer.appendChild(fragment);
}


