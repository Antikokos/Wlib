const genres = ['fantasy', 'detective', 'manga', 'romance'];

// Функция для получения случайных книг
function fetchRandomBooks(genre, containerId) {
    const url = `https://www.googleapis.com/books/v1/volumes?q=subject:${genre}&maxResults=10`; // Увеличено до 10

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById(containerId);
            container.innerHTML = ''; // Очистка контейнера перед загрузкой новых книг

            // Генерация случайных книг из полученных данных
            const randomBooks = getRandomItems(data.items, 10); // Теперь выбираем 10 книг
            randomBooks.forEach(item => {
                const title = item.volumeInfo.title || 'Без названия';
                const authors = item.volumeInfo.authors ? item.volumeInfo.authors.join(', ') : 'Неизвестные авторы';
                const imageUrl = item.volumeInfo.imageLinks ? item.volumeInfo.imageLinks.thumbnail : 'https://via.placeholder.com/200x240/444';

                const bookCard = document.createElement('div');
                bookCard.classList.add('book-card');
                bookCard.innerHTML = `
                    <div class="book-image" style="background-image: url('${imageUrl}');"></div>
                    <div class="book-info">
                        <h3>${title}</h3>
                        <p>Автор(ы): ${authors}</p>
                    </div>
                `;
                container.appendChild(bookCard);
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

// Горизонтальная прокрутка с помощью колеса мыши
genres.forEach(genre => {
    const container = document.getElementById(genre);
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        container.scrollLeft += e.deltaY;
    });
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