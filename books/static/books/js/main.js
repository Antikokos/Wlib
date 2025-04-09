const genres = ['fantasy', 'detective', 'manga', 'romance'];

// Функция для инициализации карусели
function initCarousel(genre, containerClass) {
    const books = window.bookData[`${genre}_books`] || [];
    const carousel = $(`.${containerClass}-carousel`);

    if (carousel.length === 0) {
        console.error(`Карусель для ${genre} не найдена`);
        return;
    }

    // Очищаем и заполняем карусель
    carousel.empty();

    books.forEach(book => {
        const bookCard = `
            <div class="book-card">
                <a href="/book/${book.id}">
                    <div class="book-image" style="background-image: url('${book.thumbnail}');"></div>
                    <div class="book-info">
                        <h3>${book.title}</h3>
                        <p>Автор: ${book.authors}</p>
                    </div>
                </a>
            </div>
        `;
        carousel.append(bookCard);
    });

    // Инициализация Slick Carousel
    if (carousel.hasClass('slick-initialized')) {
        carousel.slick('unslick');
    }

    carousel.slick({
        slidesToShow: Math.min(5, books.length),
        slidesToScroll: Math.min(2, books.length),
        infinite: books.length >= 5,
        prevArrow: '<button type="button" class="slick-prev">←</button>',
        nextArrow: '<button type="button" class="slick-next">→</button>',
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: Math.min(3, books.length),
                    slidesToScroll: 1
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: Math.min(2, books.length),
                    slidesToScroll: 1
                }
            }
        ]
    });
}

// Инициализация всех каруселей после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    genres.forEach(genre => {
        initCarousel(genre, genre);
    });

    // Поиск (оставьте ваш существующий код)
    const searchInput = document.querySelector('.search-txt');
    searchInput.addEventListener('input', function() {
        if (searchInput.value !== '') {
            searchInput.style.color = 'white';
            searchInput.style.backgroundColor = '#1d1f21';
        } else {
            searchInput.style.color = '';
            searchInput.style.backgroundColor = '';
        }
    });
});