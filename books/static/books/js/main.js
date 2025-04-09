const genres = ['Фантастика', 'Детектив', 'Манга', 'Романтика'];

// Функция для получения книг из локальной БД
function fetchBooksFromDB(genre, containerClass) {
    // Используем данные, которые уже переданы в шаблон Django
    const genreDataMap = {
        'fantasy': window.fantasy_books || [],
        'detective': window.detective_books || [],
        'manga': window.manga_books || [],
        'romance': window.romance_books || []
    };

    const books = genreDataMap[genre];
    const carousel = $(`.${containerClass}-carousel`);
    carousel.empty();

    books.forEach(book => {
        const bookCard = `
            <div class="book-card">
                <a href="/book/${book.id}">
                    <div class="book-image" style="background-image: url('${book.thumbnail}');"></div>
                    <div class="book-info">
                        <h3>${book.title}</h3>
                        <p>Автор: ${book.authors || 'Неизвестный автор'}</p>
                    </div>
                </a>
            </div>
        `;
        carousel.append(bookCard);
    });

    // Инициализация Slick Carousel
    carousel.slick({
        slidesToShow: Math.min(5, books.length), 
        slidesToScroll: 2,
        infinite: books.length >= 5, 
        prevArrow: "<button type='button' class='slick-prev'>&#10094;</button>",
        nextArrow: "<button type='button' class='slick-next'>&#10095;</button>",
    });
}

// Загружаем книги для каждого жанра
genres.forEach(genre => {
    fetchBooksFromDB(genre, genre);
});

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-txt');
    searchInput.focus();

    searchInput.addEventListener('input', function() {
        if (searchInput.value !== '') {
            searchInput.style.color = 'white';
            searchInput.style.backgroundColor = '#1d1f21';
        } else {
            searchInput.style.color = '';
            searchInput.style.backgroundColor = '';
        }
    });

    setTimeout(function() {
        searchInput.focus();
    }, 100);
});